from rest_framework import serializers

from app_sales_points.models import City, Warehouse, Stock


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = "__all__"


class WarehouseSerializer(serializers.ModelSerializer):
    city = CitySerializer()

    class Meta:
        model = Warehouse
        fields = "__all__"


class StockSerializer(serializers.ModelSerializer):
    warehouse = WarehouseSerializer()

    class Meta:
        model = Stock
        fields = "__all__"
