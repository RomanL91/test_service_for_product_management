import os
import re
import pika
import requests
import datetime
from decimal import Decimal

import xml.etree.ElementTree as ET

from django.db import transaction
from collections import defaultdict
from django.core.files.base import ContentFile

from app_external_products.models import (
    ExtProduct,
    ExtProductImage,
    Warehouse,
    Stock,
    Specifications,
    NameSpecifications,
    ValueSpecifications,
)


from app_products.models import Products
from app_sales_points.models import Stock as BaseStock, Warehouse as BaseWarehouse


def fetch_offers_from_kaspi():
    """
    Обращается к https://sck-1.ru/SCK_KASPI.xml,
    парсит XML и возвращает результат в виде:
      {
        "offers": [
          {
            "sku": "...",
            "model": "...",
            "brand": "...",
            "availabilities": [
              {"storeId": "...", "available": "...", "stockCount": ...},
              ...
            ],
            "cityprices": [
              {"cityId": "...", "price": ...},
              ...
            ]
          },
          ...
        ]
      }
    """
    url = "https://sck-1.ru/SCK_KASPI.xml"
    response = requests.get(url, timeout=30)
    response.raise_for_status()  # выбросит ошибку, если код ответа != 200

    # Парсим XML
    # В зависимости от версии Python можно использовать r.text или r.content
    root = ET.fromstring(response.content)

    # В XML есть пространство имён "kaspiShopping", мешающее простому поиску тегов.
    # Мы можем либо удалить префиксы, либо использовать регулярное выражение, чтобы убрать {namespace}.
    def strip_namespace(tag):
        return re.sub(r"\{.*\}", "", tag)

    offers_list = []

    # Ищем элемент <offers>
    # root имеет нескольких детей: <company>, <merchantid>, <offers>.
    for child in root:
        if strip_namespace(child.tag) == "offers":
            # Перебираем всех <offer>
            for offer_el in child:
                if strip_namespace(offer_el.tag) == "offer":
                    sku = offer_el.attrib.get("sku", "")
                    model_text = ""
                    brand_text = ""
                    availabilities = []
                    cityprices = []

                    # Перебираем дочерние узлы внутри <offer>
                    for sub_el in offer_el:
                        sub_tag = strip_namespace(sub_el.tag)

                        if sub_tag == "model":
                            model_text = sub_el.text or ""
                        elif sub_tag == "brand":
                            brand_text = sub_el.text or ""
                        elif sub_tag == "availabilities":
                            # внутри <availabilities> есть несколько <availability>
                            for av_el in sub_el:
                                if strip_namespace(av_el.tag) == "availability":
                                    store_id = av_el.attrib.get("storeId", "")
                                    available = av_el.attrib.get("available", "")
                                    stock_count = av_el.attrib.get("stockCount")

                                    # Если stockCount есть, приводим к int
                                    if stock_count is not None:
                                        stock_count = int(stock_count)
                                        availabilities.append(
                                            {
                                                "storeId": store_id,
                                                "available": available,
                                                "stockCount": stock_count,
                                            }
                                        )
                                    else:
                                        availabilities.append(
                                            {
                                                "storeId": store_id,
                                                "available": available,
                                            }
                                        )
                        elif sub_tag == "cityprices":
                            # внутри <cityprices> есть <cityprice cityId="" >...</cityprice>
                            for cp_el in sub_el:
                                if strip_namespace(cp_el.tag) == "cityprice":
                                    city_id = cp_el.attrib.get("cityId", "")
                                    price_str = cp_el.text
                                    price = int(price_str) if price_str else 0
                                    cityprices.append(
                                        {"cityId": city_id, "price": price}
                                    )

                    # Собираем оффер в итоговый словарь
                    offer_dict = {
                        "sku": sku,
                        "model": model_text,
                        "brand": brand_text,
                        "availabilities": availabilities,
                        "cityprices": cityprices,
                    }
                    offers_list.append(offer_dict)

    # Формируем финальный результат
    result = {"offers": offers_list}
    return result


def update_offers(data: dict):
    """
    Принимает данные в формате:
    {
      "offers": [
        {
          "sku": "...",
          "model": "...",
          "availabilities": [
            {
              "storeId": "...",
              "available": "yes"/"no",
              "stockCount": ...
            }
          ],
          ...
        },
        ...
      ]
    }
    Игнорируем полностью cityprices и любые другие поля, кроме вышеуказанных.
    """

    # pars_xml = fetch_offers_from_kaspi()
    # print(f"---- pars ---- >>> {pars_xml}")

    offers = data.get("offers", [])
    if not offers:
        return  # Нет данных — нечего обновлять

    # Собираем все уникальные SKU и storeId
    skus = set()
    store_ids = set()

    for offer in offers:
        skus.add(offer["sku"])
        for av in offer.get("availabilities", []):
            store_ids.add(av["storeId"])

    # ==================================
    # 1. Обновление / создание ExtProduct
    # ==================================
    existing_products_qs_base = Products.objects.filter(vendor_code__in=skus)
    # existing_products_qs = ExtProduct.objects.filter(vendor_code__in=skus).exclude(
    #     existing_products_qs_base.values_list("vendor_code", flat=True)
    # )
    existing_products_qs = ExtProduct.objects.filter(vendor_code__in=skus).exclude(
        vendor_code__in=Products.objects.filter(vendor_code__in=skus).values_list(
            "vendor_code", flat=True
        )
    )
    existing_products_map = {p.vendor_code: p for p in existing_products_qs}
    existing_products_map_base = {p.vendor_code: p for p in existing_products_qs_base}
    print(f"---- existing_products_qs ---- >>> {existing_products_qs}")
    print(f"---- existing_products_qs_base ---- >>> {existing_products_qs_base}")
    print(f"---- existing_products_map ---- >>> {existing_products_map}")
    print(f"---- existing_products_map_base ---- >>> {existing_products_map_base}")

    new_products = []
    base_prod_to_update = []
    for offer in offers:
        sku = offer["sku"]
        presence_sign_prod_base = existing_products_map_base.get(sku, False)
        presence_sign_prod = existing_products_map.get(sku, False)
        if not presence_sign_prod and not presence_sign_prod_base:
            new_products.append(
                ExtProduct(
                    vendor_code=sku,
                    product_name=offer["model"] or "",
                    # Если нужно заполнить brand/category — добавьте логику
                )
            )
        else:
            base_prod_to_update.append(presence_sign_prod_base)
    print(f"---- new_products ---- >>> {new_products}")

    ExtProduct.objects.bulk_create(new_products)
    for p in new_products:
        existing_products_map[p.vendor_code] = p

    # (При желании можно обновлять имя у уже существующих товаров через bulk_update)

    # ==================================
    # 2. Обновление / создание Warehouse
    # ==================================
    existing_store_wh_qs = Warehouse.objects.filter(external_id__in=store_ids)
    existing_store_wh_map = {w.external_id: w for w in existing_store_wh_qs}

    new_store_wh = []
    for sid in store_ids:
        if sid not in existing_store_wh_map:
            # city=None — так как города нам не нужны
            new_store_wh.append(
                Warehouse(external_id=sid, name_warehouse=sid, city=None)
            )
    Warehouse.objects.bulk_create(new_store_wh)

    for w in new_store_wh:
        existing_store_wh_map[w.external_id] = w

    # ==================================
    # 3. Обновление / создание Stock
    # ==================================
    # Будем хранить данные в структуре:
    # final_stocks[(product_id, warehouse_id)] = quantity
    #
    final_stocks = defaultdict(int)
    final_stocks_base = defaultdict(int)
    print(f"---- final_stocks ---- >>> {final_stocks}")

    # Заполняем словарь final_stocks
    for offer in offers:
        print(f"----- offer ----- {offer}")
        offer_sku = offer.get("sku")
        print(f"----- offer_sku ----- {offer_sku}")
        product = existing_products_map.get(offer_sku)
        if product is None:
            product = existing_products_map_base.get(offer_sku)
            stocks = product.stocks.all()
            availabilities = offer.get("availabilities", [])
            print(f"--- stocks --- >> {stocks}")
            print(f"--- availabilities --- >> {availabilities}")
            for available in availabilities:
                stock = stocks.filter(
                    warehouse__external_id=available["storeId"]
                ).first()
                if stock:
                    stock.quantity = available.get("stockCount", 0)
                    stock.save()
                else:
                    wh, created = BaseWarehouse.objects.get_or_create(
                        external_id=available["storeId"],
                    )
                    BaseStock.objects.create(
                        warehouse=wh,
                        product=product,
                        quantity=available.get("stockCount", 0),
                        price=0,
                        # NB ТУТ остановился и не работает
                    )
            continue
        product_id = product.id
        # print(f"----- product_id ----- {product_id}")

        for av in offer.get("availabilities", []):
            store_id = av["storeId"]
            warehouse = existing_store_wh_map[store_id]
            warehouse_id = warehouse.id
            # Если available == "yes", записываем кол-во, иначе 0
            qty = int(av.get("stockCount", 0)) if av["available"] == "yes" else 0
            final_stocks[(product_id, warehouse_id)] = qty
            print(f"---- final_stocks ---- >>> {final_stocks}")

    print(f"---- marker ---- >>> !!!!!!!!!")

    # Достаём существующие Stock для (product_id, warehouse_id), которые у нас есть
    # print(f"---- existing_products_map ---- >>> {existing_products_map}")
    # print(
    #     f"---- existing_products_map values ---- >>> {existing_products_map.values()}"
    # )
    all_product_ids = list({p.id for p in existing_products_map.values()})
    all_warehouse_ids = list({w.id for w in existing_store_wh_map.values()})

    existing_stocks_qs = Stock.objects.filter(
        product_id__in=all_product_ids, warehouse_id__in=all_warehouse_ids
    )
    existing_stock_map = {(s.product_id, s.warehouse_id): s for s in existing_stocks_qs}

    stocks_to_create = []
    stocks_to_update = []

    for (prod_id, wh_id), quantity in final_stocks.items():
        if (prod_id, wh_id) in existing_stock_map:
            # Обновляем
            st = existing_stock_map[(prod_id, wh_id)]
            st.quantity = quantity
            st.price = 0  # Раз цены мы не используем — запишем 0 или оставим как есть
            stocks_to_update.append(st)
        else:
            # Создаём
            stocks_to_create.append(
                Stock(
                    product_id=prod_id,
                    warehouse_id=wh_id,
                    quantity=quantity,
                    price=0,  # нет цен, сохраняем 0
                )
            )

    # Сохраняем всё внутри одной транзакции
    with transaction.atomic():
        if stocks_to_create:
            Stock.objects.bulk_create(stocks_to_create)

        if stocks_to_update:
            Stock.objects.bulk_update(stocks_to_update, ["quantity", "price"])


class SessionStorage:
    def __init__(self):
        self.session = None
        self.last_auth_time = None
        self.mc_sid = None  # mc-sid

    def is_session_valid(self, valid_for_seconds: int = 7200) -> bool:
        """
        Простейшая проверка актуальности сессии (по умолчанию 2 часа = 7200 секунд).
        Можно заменить или расширить логику по своему усмотрению.
        """
        if not self.last_auth_time:
            self.session = self.do_authorization()
            return False
        delta = datetime.datetime.now() - self.last_auth_time
        return delta.total_seconds() < valid_for_seconds

    def do_authorization(self):
        """
        Делает все шаги авторизации:
        1) POST на /api/p/login
        2) GET /?continue
        3) GET /oauth2/authorization/1
        + Проверочный запрос: заходит на страницу kaspi.kz/mc
        и проверяет, нет ли редиректа на логин.
        Возвращает готовый объект requests.Session или None при неудаче.
        """
        print("== Попытка авторизации в Kaspi ==")
        session = requests.Session()

        common_headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/132.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;"
                "q=0.9,image/avif,image/webp,image/apng,*/*;"
                "q=0.8,application/signed-exchange;v=b3;q=0.7"
            ),
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
        }

        # (1) Логин
        login_url = "https://idmc.shop.kaspi.kz/api/p/login"
        login_payload = {
            "_u": "program@sck-1.kz",  # Ваш логин
            "_p": "oyB9beYr4O",  # Ваш пароль
        }
        login_headers = {
            **common_headers,
            "Content-Type": "application/json",
            "Referer": "https://idmc.shop.kaspi.kz/login",
            "Origin": "https://idmc.shop.kaspi.kz",
        }

        resp_login = session.post(
            login_url, json=login_payload, headers=login_headers, allow_redirects=False
        )
        if resp_login.status_code != 200:
            print("Не удалось залогиниться (ожидали 200), код:", resp_login.status_code)
            return None

        # (2) GET /?continue
        step2_url = "https://idmc.shop.kaspi.kz/?continue"
        step2_headers = {
            **common_headers,
            "Referer": "https://idmc.shop.kaspi.kz/login",
        }
        resp_continue = session.get(
            step2_url, headers=step2_headers, allow_redirects=True
        )
        # Можно проверить resp_continue.status_code, но там часто идёт редирект

        # (3) OAuth
        oauth_url = "https://mc.shop.kaspi.kz/oauth2/authorization/1"
        oauth_headers = {
            **common_headers,
            "Referer": "https://kaspi.kz/",
        }
        resp_oauth = session.get(oauth_url, headers=oauth_headers, allow_redirects=True)

        # Проверяем наличие mc-sid
        mc_cookies = session.cookies.get_dict(domain="mc.shop.kaspi.kz")
        if "mc-sid" not in mc_cookies:
            print("mc-sid не обнаружен. Авторизация не завершена.")
            return None

        print(
            "Авторизация на mc.shop.kaspi.kz потенциально успешна. mc-sid=",
            mc_cookies["mc-sid"],
        )

        # (4) Тестовый запрос – проверяем, что мы действительно «внутри»:
        # Вместо mc.shop.kaspi.kz/ используем https://kaspi.kz/mc/ (основная страница кабинета)
        test_url = "https://kaspi.kz/mc/"
        test_resp = session.get(test_url, headers=common_headers, allow_redirects=True)

        if test_resp.status_code == 200:
            final_url = test_resp.url
            # Если нас «выкинуло» на логин, скорее всего увидим url типа idmc.shop.kaspi.kz/login
            if "idmc.shop.kaspi.kz/login" in final_url:
                print("Похоже, при заходе в личный кабинет нас перекинуло на логин.")
                return None
            else:
                print(f"Тестовый GET вернулся 200, конечный URL = {final_url}")
                print("Все проверки пройдены. Мы авторизованы.")
        else:
            print(f"Тестовый GET на {test_url} вернул статус {test_resp.status_code}.")
            return None

        return session


global_session_storage = SessionStorage()


def extract_features(data):
    result = []

    for category in data:
        features = category.get("features", [])
        for feature in features:
            # Достаём список featureValues
            fvals = feature.get("featureValues", [])
            # Превратим в список строк
            string_values = [fv.get("value", "") for fv in fvals]
            # Склеиваем через ", " (или любой другой разделитель)
            all_values_str = ", ".join(string_values)

            result.append(
                {"name": feature.get("name", ""), "featureValues": all_values_str}
            )
    return result


def create_specifications_from_list(features_list, product_id):
    """
    features_list: список вида:
      [
        {"name": "Тип", "featureValues": "LED-телевизор"},
        {"name": "Диагональ", "featureValues": "55.0 дюйм"},
        {"name": "Входы", "featureValues": "аудио, коаксиальный, AV"},  # вся строка
        ...
      ]

    product: объект ExtProduct, к которому привязываются эти Specifications.
    """

    for feature in features_list:
        name = feature.get("name", "")
        value = feature.get(
            "featureValues", ""
        )  # не разбиваем по запятой, сохраняем как есть

        # 1. Получаем или создаём NameSpecifications
        name_obj, _ = NameSpecifications.objects.get_or_create(name_specification=name)

        # 2. Получаем или создаём ValueSpecifications
        value_obj, _ = ValueSpecifications.objects.get_or_create(
            value_specification=value
        )

        # 3. Создаём (или находим) Specifications
        Specifications.objects.get_or_create(
            product_id=product_id,
            name_specification=name_obj,
            value_specification=value_obj,
        )


def get_medium_links(images):
    """
    Принимает структуру вида:
    [
      {
        "small": "...",
        "medium": "...",
        "large": "...",
        "location": "...",
        "verified": None
      },
      ...
    ]
    Возвращает список строк (URL) из поля "medium".
    Если элемент списка не словарь или не содержит "medium", пропускаем его и выводим предупреждение.
    """
    # Проверим, что images действительно список
    if not isinstance(images, list):
        print("Ошибка: ожидался список, получено:", type(images))
        return []

    medium_links = []
    for idx, item in enumerate(images):
        if not isinstance(item, dict):
            print(f"Предупреждение: элемент №{idx} не является словарём: {item}")
            continue

        medium_url = item.get("medium")
        if medium_url is None:
            print(
                f"Предупреждение: в элементе №{idx} отсутствует ключ 'medium': {item}"
            )
            continue

        medium_links.append(medium_url)

    return medium_links


def save_images_for_product(image_urls, product_id):
    """
    Загружает изображения по списку URL и создает записи ExtProductImage,
    сохраняя файлы в ImageField.

    :param image_urls: список строк-URL, например:
        ["https://example.com/image1-medium.jpg", "https://example.com/image2-medium.jpg"]
    :param product: объект ExtProduct (или product_id) -- продукт, к которому привязываем изображения
    """
    if not image_urls:
        return

    # Если у вас только product_id, можно сделать:
    # product = ExtProduct.objects.get(id=product_id)

    # Оформим всё в транзакцию — если что-то пойдёт не так, откатим все изменения
    with transaction.atomic():
        for url in image_urls:
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()  # выбросит ошибку, если статус >= 400
            except requests.RequestException as e:
                # Здесь можно записать в лог ошибку, пропустить URL и т.д.
                print(f"Не удалось скачать {url}: {e}")
                continue

            # Получаем имя файла, например, всё, что после последнего "/"
            file_name = os.path.basename(
                url.split("?")[0]
            )  # отбрасываем параметры ?format=...
            if not file_name:
                # Если URL заканчивается на '/', можно подставить какое-то дефолтное имя
                file_name = "image.jpg"

            # Создаём в памяти «файл» для Django
            content = ContentFile(response.content)

            # Создаём объект ExtProductImage
            # Передаём в image = (ContentFile, имя_файла)
            image_obj = ExtProductImage(product_id=product_id)
            image_obj.image.save(file_name, content, save=True)
            # save=True приводит к немедленному сохранению файла на диск и записи модели в базу

            # Если нужно добавить ещё логику (например, выводить сообщения):
            print(f"Сохранено изображение: {file_name}")


def get_price(availabilities, cityInfo, product_id):
    data = {}
    for stock in availabilities:
        name_point = stock.get("name")
        city_id = stock.get("cityId")
        data.setdefault("name", name_point)
        data.setdefault("cityId", city_id)

        for info in cityInfo:
            if info["id"] == city_id:
                warehouse = Warehouse.objects.filter(external_id=name_point).first()
                data.setdefault("price", info["price"])
                data.setdefault("warehouse_pk", warehouse.pk)

                stock, created = Stock.objects.get_or_create(
                    warehouse_id=data["warehouse_pk"],
                    product_id=product_id,
                    defaults={"price": Decimal(data["price"])},
                )

                if not created:
                    stock.price = data["price"]
                    stock.save()
                data = {}


def send_message_rmq(
    message: str = "Тестовое сообщение от producer.",
    queue_name: str = "swap_info_kaspi",
    host: str = "185.100.67.246",
    port: int = 5672,
    username: str = "guest",
    password: str = "guest",
):
    """
    Функция для отправки тестового сообщения в очередь 'swap_info_kaspi'.
    """
    # Устанавливаем соединение с RabbitMQ (замените 'localhost' на нужный адрес при необходимости)
    credentials = pika.PlainCredentials(username, password)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=host, port=port, credentials=credentials)
    )
    channel = connection.channel()

    # Объявляем очередь, если она еще не создана
    channel.queue_declare(queue=queue_name)

    # Отправляем сообщение в очередь
    channel.basic_publish(exchange="", routing_key=queue_name, body=message)
    print("Отправлено сообщение:", message)

    # Закрываем соединение
    connection.close()
