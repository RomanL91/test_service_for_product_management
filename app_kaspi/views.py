from rest_framework import viewsets
from rest_framework.response import Response

from app_kaspi.models import Customer, Order, Product
from app_kaspi.serializers import CustomerSerializer, OrderSerializer, ProductSerializer


class BaseFlatViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Базовый класс для viewsets с методом list, возвращающим плоский список.
    """

    # Атрибут для указания поля, по которому нужно делать values_list
    flat_field = None

    def list(self, request, *args, **kwargs):
        if not self.flat_field:
            raise ValueError("flat_field должен быть задан в подклассе")
        queryset = self.filter_queryset(self.get_queryset()).values_list(
            self.flat_field,
            flat=True,
        )
        return Response(queryset)


class CustomerViewSet(BaseFlatViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    flat_field = "customer_id"


class OrderViewSet(BaseFlatViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    flat_field = "order_id"


class ProductViewSet(BaseFlatViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    flat_field = "product_id"
