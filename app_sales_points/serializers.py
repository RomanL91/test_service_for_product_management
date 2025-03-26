from decimal import Decimal
from datetime import date, timedelta

from rest_framework import serializers

from app_sales_points.models import City, Warehouse, Stock, Edges

from app_sales_points.utils import StockUpdater


class CitySerializer(serializers.ModelSerializer):
    total_products = serializers.IntegerField(read_only=True)
    # total_quality = serializers.IntegerField(read_only=True)

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


class StocksByCityField(serializers.Field):
    def get_discount(self, obj):
        """
        Приоритет: товар → категория → бренд.
        Возвращаем объект скидки (или None).
        """
        product_discounts = getattr(obj, "prefetched_product_discounts", [])
        if product_discounts:
            return max(product_discounts, key=lambda d: d.amount)
        cat_discounts = []
        if obj.category:
            cat_discounts = getattr(obj.category, "prefetched_category_discounts", [])
            if cat_discounts:
                return max(cat_discounts, key=lambda d: d.amount)
        brand_discounts = []
        if obj.brand:
            brand_discounts = getattr(obj.brand, "prefetched_brand_discounts", [])
            if brand_discounts:
                return max(brand_discounts, key=lambda d: d.amount)
        return None

    def to_representation(self, product):
        # 1) Получаем саму скидку (obj), если есть
        discount_obj = self.get_discount(product)  # возвращает объект скидки или None
        discount_amount = discount_obj.amount if discount_obj else 0
        discount_decimal = Decimal(discount_amount)
        if not hasattr(product, "prefetched_stocks"):
            return {}

        stocks_by_city = {}
        stock_updater = StockUpdater(stocks_by_city)

        for stock in product.prefetched_stocks:
            warehouse = getattr(stock, "warehouse", None)
            if not warehouse:
                continue  # Пропускаем объект, если нет склада
            city_name = warehouse.city.name_city
            price_before = stock.price * (1 + discount_decimal / 100)
            stocks_by_city[city_name] = {
                "price": stock.price,
                "price_before_discount": float(price_before),
                "quantity": stock.quantity,
                "edge": False,
                "transportation_cost": None,
                "estimated_delivery_days": None,
            }
            # Логика ребер
            if hasattr(product.category, "related_edges"):
                stock_updater.update_from_edges(
                    product.category.related_edges, stock, city_name, discount_decimal
                )
            if hasattr(product.brand, "related_edges"):
                stock_updater.update_from_edges(
                    product.brand.related_edges, stock, city_name, discount_decimal
                )

        return stocks_by_city
