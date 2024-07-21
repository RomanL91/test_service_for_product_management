import requests
from celery import shared_task

from django.conf import settings


class ProductDataHandler:
    BASE_URL_ETL_1C = settings.BASE_URL_ETL_1C
    BASE_URL_API_SELF = settings.BASE_URL_API_SELF

    def __init__(self, action_type):
        self.action_type = action_type
        self.url_1c = self.BASE_URL_ETL_1C + f"get_for_{action_type}/"
        self.http_method = requests.post if action_type == "create" else requests.patch

    def fetch_data(self):
        # Отправка GET запроса для получения данных
        response = requests.get(self.url_1c)
        response.raise_for_status()  # Проверка на ошибки HTTP
        return response.json()

    def send_data(self, data):
        # Отправка данных в целевой API
        result = self.http_method(self.BASE_URL_API_SELF, json=data)
        result.raise_for_status()  # Проверка на ошибки HTTP
        return result

    def process_external_products(self):
        try:
            data = self.fetch_data()
            result = self.send_data(data)
            print(f"Task completed: {self.action_type} --->>>> {result}")
        except Exception as e:
            print(f"Error during task execution: {e}")
            return {"error": str(e)}

        return {"status_code": result.status_code, "response_body": result.json()}


@shared_task(bind=True, name="Искать/добавить новые продукты")
def create_products_and_stocks(self):
    handler = ProductDataHandler("create")
    handler.process_external_products()


@shared_task(bind=True, name="Актуализировать данные о ценах/остаках")
def update_stocks(self):
    handler = ProductDataHandler("update")
    handler.process_external_products()
