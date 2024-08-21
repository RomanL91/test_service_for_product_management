import requests

from django.conf import settings


class OrdersApiAdapter:
    def __init__(self, page=1, size=1):
        self.page = page
        self.size = size
        self.host = settings.BASKET_HOST
        self.port = settings.BASKET_PORT

    def get_order_by_uuid(self, uuid_id):
        url = settings.API_URL_GET_INFO_ORDER_WITH_BASKET.format(
            basket_host=self.host,
            basket_port=self.port,
            uuid_id=uuid_id,
        )
        return self._make_get_request(url)

    def update_urder_by_uuid(self, uuid_id, **data_update):
        url = settings.API_URL_UPDATE_ORDER.format(
            basket_host=self.host,
            basket_port=self.port,
            uuid_id=uuid_id,
        )
        return self._make_patch_requests(url, **data_update)

    def get_orders(self):
        url = settings.API_URL_GET_ORDERS.format(
            basket_host=self.host,
            basket_port=self.port,
            page=self.page,
            size=self.size,
        )
        return self._make_get_request(url)

    def get_manager_archive_orders(self, manager_id):
        url = settings.API_URL_GET_ARCHIVE_ORDERS_MANAGER.format(
            basket_host=self.host,
            basket_port=self.port,
            id_manager=manager_id,
            page=self.page,
            size=self.size,
        )
        return self._make_get_request(url)

    def _make_get_request(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return {}

    def _make_patch_requests(self, url, **data):
        response = requests.patch(url, json=data)
        return response.status_code, response.json()
