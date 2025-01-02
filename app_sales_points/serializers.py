from datetime import date, timedelta

from rest_framework import serializers

from app_sales_points.models import City, Warehouse, Stock, Edges


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


# Сериализатор для Edges
class EdgeSerializer(serializers.ModelSerializer):
    city_from = serializers.StringRelatedField()
    city_to = serializers.StringRelatedField()
    estimated_delivery_days = serializers.IntegerField(read_only=True)
    estimated_delivery_date = serializers.SerializerMethodField()
    transportation_cost = serializers.FloatField()

    class Meta:
        model = Edges
        fields = [
            "city_from",
            "city_to",
            "estimated_delivery_days",
            "estimated_delivery_date",
            "transportation_cost",
            "is_active",
            "expiration_date",
        ]

    def get_estimated_delivery_date(self, obj):
        if obj.estimated_delivery_days:
            self.estimated_delivery_date = date.today() + timedelta(
                days=obj.estimated_delivery_days
            )
            return self.estimated_delivery_date
        return 0
