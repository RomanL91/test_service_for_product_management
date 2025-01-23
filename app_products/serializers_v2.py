from rest_framework import serializers
from rest_framework.reverse import reverse

from app_products.models import Products, ProductImage

from app_sales_points.serializers import EdgeSerializer, StocksByCityField
from app_brands.serializers import BrandSerializer
from app_manager_tags.serializers import TagSerializer
from app_reviews.serializers import ReviewsForProductsSerializer
from app_specifications.serializers import SpecificationsSerializer
from app_category.serializers_v2 import CategorySerializer
from app_descriptions.serializers import ProductDescriptionSerializer


# Сериализатор для ProductImage
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image"]  # Только поле изображения


class DiscountShortSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    description = serializers.CharField()


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
    reviews = serializers.SerializerMethodField()  # Ограничиваем отзывы через метод
    reviews_url = serializers.SerializerMethodField()  # Ссылка на отзывы к продукту
    # desc_url = serializers.SerializerMethodField()  # Ссылка на описание к продукту
    description = ProductDescriptionSerializer(read_only=True)
    related_products_url = (
        serializers.SerializerMethodField()
    )  # Ссылка на связанные продукты
    configuration_url = serializers.SerializerMethodField()  # Ссылка на конфигурации
    discount = serializers.SerializerMethodField()

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
            "discount",
            "tags",
            "specifications",
            "reviews",
            "reviews_url",
            # "desc_url",
            "description",
            "related_products_url",
            "configuration_url",
        ]

    def get_reviews(self, obj):
        """
        Возвращает только первые 20 отзывов.
        """
        if hasattr(obj, "reviews"):
            # Ограничиваем первые 20 отзывов
            limited_reviews = obj.reviews.all()[:20]
            return ReviewsForProductsSerializer(limited_reviews, many=True).data
        return []

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

    # def get_desc_url(self, obj):
    #     request = self.context.get("request")
    #     return reverse("all_desc_to_product", args=[obj.id], request=request)

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

    def get_discount(self, obj):
        """
        1) Если есть скидка на товар - вернуть её (max)
        2) Иначе смотреть скидку на категорию
        3) Иначе скидку на бренд
        """
        # 1) Скидки на товар
        product_discounts = getattr(obj, "prefetched_product_discounts", [])
        if product_discounts:
            # Вернуть  максимальную
            disc = max(product_discounts, key=lambda d: d.amount)
            return self._serialize_discount(disc)

        # 2) Скидки на категорию
        cat_discounts = []
        if obj.category:
            cat_discounts = getattr(obj.category, "prefetched_category_discounts", [])
        if cat_discounts:
            disc = max(cat_discounts, key=lambda d: d.amount)

            return self._serialize_discount(disc)

        # 3) Скидки на бренд
        brand_discounts = []
        if obj.brand:
            brand_discounts = getattr(obj.brand, "prefetched_brand_discounts", [])
        if brand_discounts:
            disc = max(brand_discounts, key=lambda d: d.amount)

            return self._serialize_discount(disc)

        # Нет скидок
        return None

    def _serialize_discount(self, disc):
        """Переводим объект скидки в удобный JSON."""
        serializer = DiscountShortSerializer(disc)
        return serializer.data
