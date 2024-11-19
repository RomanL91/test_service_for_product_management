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


class PriceRangeByCitySerializer(serializers.Serializer):
    city = serializers.CharField(
        source="warehouse__city__name_city",
        read_only=True,
    )
    min_price = serializers.DecimalField(
        source="MinPrice",
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )
    max_price = serializers.DecimalField(
        source="MaxPrice",
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )


class StockSerializerElasticSearch(serializers.Serializer):
    city = serializers.CharField()
    quantity = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
