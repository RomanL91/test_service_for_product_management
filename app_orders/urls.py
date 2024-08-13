from django.urls import path
from .views import OrdersListView, OrderDetailView

urlpatterns = [
    path("orders/", OrdersListView.as_view(), name="orders_list"),
    path("order/<uuid:uuid_id>/", OrderDetailView.as_view(), name="order-detail"),
]
