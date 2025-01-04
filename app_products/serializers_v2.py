from rest_framework import serializers
from rest_framework.reverse import reverse

from app_products.models import Products, ProductImage

from app_sales_points.serializers import EdgeSerializer, StocksByCityField
from app_brands.serializers import BrandSerializer
from app_manager_tags.serializers import TagSerializer
from app_specifications.serializers import SpecificationsSerializer
from app_category.serializers_v2 import CategorySerializer


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
    stocks = StocksByCityField(source="*")  # Поле для остатков по городам
    category = CategorySerializer(read_only=True)  # Информация о категории
    brand = BrandSerializer(read_only=True)  # Информация о бренде
    tags = TagSerializer(
        many=True, read_only=True, source="prefetched_tags"
    )  # Теги продукта
    specifications = SpecificationsSerializer(
        many=True, read_only=True, source="prefetched_specifications"
    )  # Характеристики
    reviews_url = serializers.SerializerMethodField()  # Ссылка на отзывы к продукту
    desc_url = serializers.SerializerMethodField()  # Ссылка на описание к продукту
    related_products_url = (
        serializers.SerializerMethodField()
    )  # Ссылка на связанные продукты
    configuration_url = serializers.SerializerMethodField()  # Ссылка на конфигурации

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
            "stocks",
            "tags",
            "specifications",
            "desc_url",
            "reviews_url",
            "related_products_url",
            "configuration_url",
        ]

    #
    # ========== Вспомогательный метод для формирования URL с ?ids=... ==========
    #
    def _build_filter_by_ids_url(
        self, items, request, url_name="products-filter-by-ids"
    ):
        """
        Обобщённый метод:
          - items: список объектов (например, obj.prefetched_related_products)
          - request: объект запроса, нужен для reverse()
          - url_name: имя маршрута, по умолчанию "products-filter-by-ids"
        Возвращает строку вида:  <base_url>?ids=1,2,3
        """
        if not request:
            return None
        base_url = reverse(url_name, request=request)
        if not items:
            return f"{base_url}?ids="
        ids_param = ",".join(str(item.pk) for item in items)
        return f"{base_url}?ids={ids_param}"

    def get_related_edges(self, obj):
        if hasattr(obj.brand, "related_edges") or hasattr(
            obj.category, "related_edges"
        ):
            edges_cat = getattr(obj.category, "related_edges", [])
            edges_brand = getattr(obj.brand, "related_edges", [])
            edges_brand.extend(edges_cat)
            return EdgeSerializer(edges_brand, many=True).data
        return []

    def get_reviews_url(self, obj):
        request = self.context.get("request")
        return reverse("all_reviews_to_product", args=[obj.id], request=request)

    def get_desc_url(self, obj):
        request = self.context.get("request")
        return reverse("all_desc_to_product", args=[obj.id], request=request)

    #
    # ========== Методы для related_products_url и configuration_url ==========
    #
    def get_related_products_url(self, obj):
        # Вместо повторения кода, вызываем _build_filter_by_ids_url
        related_list = getattr(obj, "prefetched_related_products", [])
        request = self.context.get("request")
        return self._build_filter_by_ids_url(related_list, request)

    def get_configuration_url(self, obj):
        config_list = getattr(obj, "prefetched_configuration", [])
        request = self.context.get("request")
        return self._build_filter_by_ids_url(config_list, request)
