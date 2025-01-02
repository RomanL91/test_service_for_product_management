from rest_framework import serializers
from rest_framework.reverse import reverse

from app_products.models import Products, ProductImage

from app_sales_points.serializers import EdgeSerializer
from app_brands.serializers import BrandSerializer
from app_manager_tags.serializers import TagSerializer
from app_category.serializers_v2 import CategorySerializer

from app_products.utils import StockUpdater


# Сериализатор для ProductImage
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image"]  # Только поле изображения


# Сериализатор для Products
class ProductSerializer(serializers.ModelSerializer):
    related_edges = serializers.SerializerMethodField()  # Поле для ребер
    images = ProductImageSerializer(many=True, read_only=True)  # Изображения
    avg_rating = serializers.FloatField(read_only=True)  # Средний рейтинг
    reviews_count = serializers.IntegerField(read_only=True)  # Количество отзывов
    stocks = serializers.SerializerMethodField()  # Поле для остатков по городам
    category = CategorySerializer(read_only=True)  # Информация о категории
    brand = BrandSerializer(read_only=True)  # Информация о бренде
    tag_prod = TagSerializer(many=True, read_only=True)  # Теги продукта
    specifications = serializers.SerializerMethodField()  # Характеристики
    reviews_url = serializers.SerializerMethodField()  # Ссылка на отзывы к продукту
    desc_url = serializers.SerializerMethodField()  # Ссылка на описание к продукту

    class Meta:
        model = Products
        fields = [
            "id",
            "vendor_code",
            "slug",
            "name_product",
            "additional_data",
            "category",
            "brand",
            "images",
            "related_edges",
            "avg_rating",
            "reviews_count",
            "reviews_url",
            "stocks",
            "tag_prod",
            "specifications",
            "desc_url",
        ]

    def get_related_edges(self, obj):
        # Проверяем, если у категории или бренда есть аннотированные ребра
        if hasattr(obj.brand, "related_edges") or hasattr(
            obj.category, "related_edges"
        ):
            edges_cat = obj.category.related_edges
            edges_brand = obj.brand.related_edges
            edges_brand.extend(edges_cat)
            return EdgeSerializer(edges_brand, many=True).data
        return []

    def get_stocks(self, obj):
        # Проверяем, если у продукта есть аннотированные остатки или ребра
        if hasattr(obj, "prefetched_stocks"):
            stocks_by_city = {}
            stock_updater = StockUpdater(stocks_by_city)
            # Инициализация информации о запасах по городам
            for stock in obj.prefetched_stocks:
                city_name = stock.warehouse.city.name_city
                stocks_by_city[city_name] = {
                    "price": stock.price,
                    "quantity": stock.quantity,
                    "edge": False,
                    "transportation_cost": None,
                    "estimated_delivery_days": None,
                }
                # Обновление запасов на основе ребер категории
                if hasattr(obj.category, "related_edges"):
                    stock_updater.update_from_edges(
                        obj.category.related_edges, stock, city_name
                    )

                # Обновление запасов на основе ребер бренда
                if hasattr(obj.brand, "related_edges"):
                    stock_updater.update_from_edges(
                        obj.brand.related_edges, stock, city_name
                    )
            return stocks_by_city

        return {}

    def get_specifications(self, obj):
        # Преобразуем аннотированные спецификации в нужный формат
        if hasattr(obj, "prefetched_specifications"):
            return {
                spec.name_specification.name_specification: spec.value_specification.value_specification
                for spec in obj.prefetched_specifications
            }
        return {}

    def get_reviews_url(self, obj):
        request = self.context.get("request")
        return reverse("all_reviews_to_product", args=[obj.id], request=request)

    def get_desc_url(self, obj):
        request = self.context.get("request")
        return reverse("all_desc_to_product", args=[obj.id], request=request)
