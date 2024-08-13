import requests

from django.views.generic import ListView, DetailView

from django.conf import settings


class OrdersListView(ListView):
    template_name = "app_orders/orders_list.html"
    context_object_name = "orders"
    paginate_by = 1

    # raise ImproperlyConfigured если не переопределить данный метод.
    # Он вызывается по умолчанию.
    def get_queryset(self):
        return []

    def get_data_from_api(self):
        # Получаем данные из API
        page = self.request.GET.get("page", 1)
        size = self.paginate_by
        url = settings.API_URL_GET_ORDERS.format(page=page, size=size)
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            # Возвращаем все для использования в get_context_data
            return data
        return {}

    def get_context_data(self, **kwargs):
        # context = super().get_context_data(**kwargs)
        context = {}
        data = self.get_data_from_api()
        context["orders"] = data.get("items", [])
        context["total"] = data.get("total", 0)
        context["page"] = data.get("page", 1)
        context["size"] = data.get("size", 1)
        context["pages"] = data.get("pages", 1)
        context["is_paginated"] = context["pages"] > 1

        return context


class OrderDetailView(DetailView):
    template_name = "app_orders/order_detail.html"
    context_object_name = "order"

    def get_object(self):
        uuid_id = self.kwargs.get("uuid_id")
        url = settings.API_URL_GET_INFO_ORDER_WITH_BASKET.format(uuid_id=uuid_id)
        response = requests.get(
            url
        )
        if response.status_code == 200:
            return response.json()
        return None
