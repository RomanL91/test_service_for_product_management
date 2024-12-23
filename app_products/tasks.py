import requests, json
from celery import shared_task

from django.conf import settings


class ProductDataHandler:
    BASE_URL_ETL_1C = settings.BASE_URL_ETL_1C
    BASE_URL_API_SELF = settings.BASE_URL_API_SELF

    def __init__(self, action_type):
        self.action_type = action_type
        self.partial_data = ""
        self.url_1c = self.BASE_URL_ETL_1C + f"get_for_{action_type}/"
        self.http_method = requests.post if action_type == "create" else requests.patch

    def fetch_data(self, chunk_size=65536):
        with requests.get(self.url_1c, stream=True) as response:
            # Проверяем успешность запроса
            response.raise_for_status()

            # Читаем данные чанками
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:  # Пропускаем пустые чанки
                    yield chunk

    def send_data(self, data_stream):
        try:
            headers = {"Content-Type": "application/json", "Host": "localhost"}

            # Аккумулируем чанки данных в строку
            for chunk in data_stream:
                # Преобразуем байты в строку, если это необходимо
                chunk_str = chunk.decode("utf-8") if isinstance(chunk, bytes) else chunk
                self.partial_data += chunk_str

                # Если мы находим полный JSON-объект, парсим его
                try:
                    # Попробуем распарсить строку как JSON
                    data = json.loads(self.partial_data)

                    # Если парсинг успешен, отправляем данные
                    response = self.http_method(
                        self.BASE_URL_API_SELF, json=data, headers=headers
                    )
                    response.raise_for_status()  # Проверяем успешность запроса
                    print(f"Data sent successfully: {response.text}")

                    # Очистим строку для следующего чанка
                    self.partial_data = ""
                except json.JSONDecodeError:
                    # Если данные не могут быть распарсены, продолжаем собирать данные
                    continue
                except requests.exceptions.RequestException:
                    return 1
            return 0
        except Exception:
            return 1

    def process_external_products(self):
        try:
            data = self.fetch_data()
            result = self.send_data(data)
            print(f"Task completed: {self.action_type} --->>>> {result}")
            return result
        except Exception as e:
            print(f"Error during task execution: {e}")
            return {"error": str(e)}


@shared_task(bind=True, name="Искать/добавить новые продукты")
def create_products_and_stocks(self):
    handler = ProductDataHandler("create")
    handler.process_external_products()


@shared_task(bind=True, name="Актуализировать данные о ценах/остаках")
def update_stocks(self):
    handler = ProductDataHandler("update")
    handler.process_external_products()
