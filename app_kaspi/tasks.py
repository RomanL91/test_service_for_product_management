import pytz
import requests

from time import time
from datetime import datetime
from celery import shared_task

from django.conf import settings

from app_kaspi.models import (
    Token,
    Customer,
    Product,
    Products,
    Order,
)


@shared_task(bind=True, name="Проверить появление АРХИВНЫХ заявок")
def receive_new_applications(
    self,
    number="0",
    size="100",
    time_back_min="5",
    url_service_etl=settings.ETL_SERVICE_GET_ARCHIVE_ORDERS_KASPI,
    kaspi_token=None,
):
    try:
        current_time_seconds = time()
        # Вычитаем time_back_min минут (time_back_min минут * 60 секунд в минуте)
        time_minus_5_minutes = current_time_seconds - (int(time_back_min) * 60)
        # Преобразование в миллисекунды
        current_time_milliseconds_5_minutes_ago = int(time_minus_5_minutes * 1000)
        # формируем квери с которыми ETL обратиться к Каспи
        params = {
            "page[size]": size,
            "page[number]": number,
            "filter[orders][creationDate][$ge]": current_time_milliseconds_5_minutes_ago,
            "include[orders]": "entries",
            "filter[orders][state]": "ARCHIVE",  # or ARCHIVE or NEW
        }

        # далее достаем первый токен, которой доступен в системе как активный
        if kaspi_token is None:
            kaspi_token = Token.objects.filter(is_active=True).first().token_value
        # формируем инфу для ПОСТ запроса к ЕТЛ
        data_post = {
            "kaspi_token": kaspi_token,
            "params": params,
            "orders_api": settings.ORDERS_API,
        }
        # запрос
        response = requests.post(url=url_service_etl, json=data_post)
        data_response = response.json()
        data_customers = data_response.get("customers", [])
        data_orderentries = data_response.get("orderentries", [])
        data_orderds = data_response.get("self_order", [])

        # ===== блок работы с ответом от ETL =====
        new_customers = []
        for customer in data_customers:
            new_customers.append(
                Customer(
                    customer_id=customer["attributes_customer_id"],
                    cell_phone=customer["attributes_customer_cellPhone"],
                    first_name=customer["attributes_customer_firstName"],
                    last_name=customer["attributes_customer_lastName"],
                )
            )
        customers = Customer.objects.bulk_create(new_customers)

        # тут устанавливаю связь продукта каспи и продукта системы
        vendor_codes = [el["code"] for el in data_orderentries]
        # Сначала нужно получить объекты Products, соответствующие этим кодам
        products = Products.objects.filter(vendor_code__in=vendor_codes)
        # Создаем словарь для быстрого доступа к продуктам по их vendor_code
        products_dict = {product.vendor_code: product for product in products}
        # обхожу ордера, готовлю список сохранния продуктов
        new_orderentries = []
        for product_kaspi in data_orderentries:
            new_orderentries.append(
                Product(
                    product_id=product_kaspi["id"],
                    name=product_kaspi["name"],
                    prod_in_shop=products_dict.get(product_kaspi["code"], None),
                    base_price=product_kaspi["basePrice"],
                    vendor_code=product_kaspi["code"],
                )
            )
        # сохраняю пакет информацией о продуктах каспи
        kaspi_prod = Product.objects.bulk_create(new_orderentries)
        # получаю ИД пользователей из ордеров
        customers_ids = [order["attributes_customer_id"] for order in data_orderds]
        # получаю инстансы пользователей из системы
        customers_filter = Customer.objects.filter(customer_id__in=customers_ids)
        # создаю удобную структуру информации для взятия инстанса по ключу
        customers_dict = {
            customer.customer_id: customer for customer in customers_filter
        }
        # получаю ИД продуктов из ордеров
        product_ids = [f"{el['id']}IyMw" for el in data_orderds]
        # получаю инстансы продуктов каспи из системы
        product_filter = Product.objects.filter(product_id__in=product_ids)
        # создаю удобную структуру информации для взятия инстанса по ключу
        products_dict_to_order = {
            product.product_id: product for product in product_filter
        }
        # подготовка списка для сохранения ордеров
        new_self_order = []
        for el in data_orderds:
            prod = products_dict_to_order.get(f"{el['id']}IyMw", None)
            cust = customers_dict.get(el["attributes_customer_id"], None)
            # конвертируем Unix epoch для creation_date
            dt_creation_date = datetime.fromtimestamp(
                el["attributes_creationDate"], pytz.UTC
            )
            creation_date = dt_creation_date.astimezone(
                pytz.timezone(settings.TIME_ZONE)
            )
            # конвертируем Unix epoch для approved_by_bank_date
            dt_approved_by_bank_date = datetime.fromtimestamp(
                el["attributes_approvedByBankDate"], pytz.UTC
            )
            approved_by_bank_date = dt_approved_by_bank_date.astimezone(
                pytz.timezone(settings.TIME_ZONE)
            )

            new_self_order.append(
                Order(
                    order_id=el["id"],
                    code=el["attributes_code"],
                    total_price=el["attributes_totalPrice"],
                    payment_mode=el["attributes_paymentMode"],
                    creation_date=creation_date,
                    delivery_cost_for_seller=el["attributes_deliveryCostForSeller"],
                    is_kaspi_delivery=el["attributes_isKaspiDelivery"],
                    delivery_mode=el["attributes_deliveryMode"],
                    pre_order=el["attributes_preOrder"],
                    state=el["attributes_state"],
                    approved_by_bank_date=approved_by_bank_date,
                    status=el["attributes_status"],
                    product_in_orders=prod,
                    customer_kaspi=cust,
                    delivery_address=el["attributes_deliveryAddress_formattedAddress"],
                    latitude=el["attributes_deliveryAddress_latitude"],
                    longitude=el["attributes_deliveryAddress_longitude"],
                )
            )
        orders = Order.objects.bulk_create(new_self_order)

        return response.json()
    except Exception as e:
        return {"Error": e}
