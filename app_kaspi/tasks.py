import requests
from time import time
from celery import shared_task

from django.conf import settings


sub_url_1 = "https://kaspi.kz/shop/api/v2/orderentries/{base_id_order}IyMw/product"

sub_url_2 = "https://kaspi.kz/shop/api/v2/orders/{base_id_order}/entries"


@shared_task(bind=True, name="Проверить появление НОВЫХ заявок")
def receive_new_applications(
    self,
    number="0",
    size="100",
    time_back_min="5",
    url_template_base="https://kaspi.kz/shop/api/v2/orders?page[number]={number}&page[size]={size}&filter[orders][state]=NEW&filter[orders][creationDate][$ge]={creationDate}&include[orders]=user",
    url_template_product="https://kaspi.kz/shop/api/v2/orderentries/{base_id_order}IyMw/product",
    url_template_entries="https://kaspi.kz/shop/api/v2/orders/{base_id_order}/entries",
    url_service_etl="",  # нужно указать!
    kaspi_token="",  # нужно указать!
):
    current_time_seconds = time()
    # Вычитаем 5 минут (5 минут * 60 секунд в минуте)
    time_minus_5_minutes = current_time_seconds - (int(time_back_min) * 60)
    # Преобразование в миллисекунды
    current_time_milliseconds_5_minutes_ago = int(time_minus_5_minutes * 1000)

    complited_base_url = url_template_base.format(
        number=number, size=size, creationDate=current_time_milliseconds_5_minutes_ago
    )

    print(complited_base_url)

    # далее достаем первый токен, которой доступен в системе как активный
    # формируем ПОСТ запрос к ЕТЛ с данными: шаблоны, токен
    # ЕТЛ запрашивает у сервака инфу о Customer Address Product KaspiDelivery в виде плоских списков
    # ЕТЛ принимает данные, делает 1 синхронный запрос на complited_base_url
    # получает список с объектами, содержащие base_id_order и формирует или сразу
    # делает 2 асинхронных подзапроса на url_template_product и url_template_entries

    return complited_base_url
