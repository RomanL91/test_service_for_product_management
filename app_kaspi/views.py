from rest_framework import serializers
from .models import Customer, Address, Order, Product


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    delivery_address = AddressSerializer(read_only=True)

    class Meta:
        model = Order
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


from rest_framework import viewsets
from .models import Customer, Address, Order, Product

# from .serializers import CustomerSerializer, AddressSerializer, OrderSerializer, ProductSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
