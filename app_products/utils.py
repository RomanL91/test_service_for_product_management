import os
import re
import requests
import datetime
from decimal import Decimal

import xml.etree.ElementTree as ET

from django.db import transaction
from collections import defaultdict
from django.core.files.base import ContentFile

from app_specifications.models import (
    NameSpecifications,
    ValueSpecifications,
    Specifications,
)

from app_products.models import Products, ProductImage
from app_sales_points.models import Stock as BaseStock, Warehouse as BaseWarehouse


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
            image_obj = ProductImage(product_id=product_id)
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
                warehouse = BaseWarehouse.objects.filter(external_id=name_point).first()
                data.setdefault("price", info["price"])
                data.setdefault("warehouse_pk", warehouse.pk)

                stock, created = BaseStock.objects.get_or_create(
                    warehouse_id=data["warehouse_pk"],
                    product_id=product_id,
                    defaults={"price": Decimal(data["price"])},
                )

                if not created:
                    stock.price = data["price"]
                    stock.save()
                data = {}
