import requests

from django.views.generic import ListView, DetailView
from django.http import HttpResponseRedirect
from django.conf import settings

from app_orders.OrdersApiAdapter import OrdersApiAdapter


class OrdersListView(ListView):
    template_name = "app_orders/orders_list.html"
    context_object_name = "orders"
    paginate_by = 1

    def get_queryset(self):
        return []

    def get_context_data(self, **kwargs):
        # context = super().get_context_data(**kwargs)
        context = {}

        page = self.request.GET.get("page", 1)
        size = self.paginate_by
        adapter = OrdersApiAdapter(page=page, size=size)

        # Получаем ID менеджера (может быть получен, например, из request.user)
        manager_id = self.request.user.id

        if self.request.resolver_match.url_name == "archive_orders_list":
            manager_id = (
                self.request.user.id
            )  # Используем текущего пользователя как менеджера
            data = adapter.get_manager_archive_orders(manager_id)
        else:
            data = adapter.get_orders()

        context["orders"] = data.get("items", [])
        context["object_list"] = data.get("items", [])
        context["total"] = data.get("total", 0)
        context["page"] = data.get("page", 1)
        context["size"] = data.get("size", 1)
        context["pages"] = data.get("pages", 1)
        context["is_paginated"] = context["pages"] > 1

        return context

    def archive_list_view(self, request, *args, **kwargs):
        # Специфическая логика для отображения архивных заказов
        manager_id = kwargs.get("pk")  # Получаем ID менеджера из URL
        context = self.get_context_data(archive=True, manager_id=manager_id)
        return self.render_to_response(context)


class OrderDetailView(DetailView):
    template_name = "app_orders/order_detail.html"
    context_object_name = "order"
    adapter = OrdersApiAdapter()

    def get_object(self):
        uuid_id = self.kwargs.get("uuid_id")
        self.adapter = OrdersApiAdapter()
        return self.adapter.get_order_by_uuid(uuid_id)

    def post(self, request, *args, **kwargs):
        uuid_id = self.kwargs.get("uuid_id")

        data = {
            "order_status": request.POST.get("order_status"),
            "manager_executive": request.POST.get("manager_executive"),
            "manager_executive_id": request.POST.get("manager_executive_id"),
            "manager_mailbox": request.POST.get("manager_mailbox"),
        }

        resp_status_code, resp_data = self.adapter.update_urder_by_uuid(uuid_id, **data)
        if resp_status_code == 200:
            return HttpResponseRedirect(request.path_info)
        return self.render_to_response(
            self.get_context_data(order=self.get_object(), error=resp_data)
        )
