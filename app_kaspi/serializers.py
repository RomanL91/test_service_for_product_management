from rest_framework import serializers

from app_kaspi.models import Customer, Order, Product


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)

    class Meta:
        model = Order
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
