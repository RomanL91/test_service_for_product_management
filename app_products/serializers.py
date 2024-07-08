from typing import List

from django.db.models import Min

from rest_framework import serializers

from app_products.models import Products, ProductImage, PopulatesProducts
from app_sales_points.models import Stock
from app_specifications.models import Specifications

from app_category.serializers import CategorySerializer
from app_brands.serializers import BrandsSerializer
from app_manager_tags.serializers import TagSerializer
from app_specifications.serializers import SpecificationsSerializer
from app_services.serializers import ServiceSerializer


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = "__all__"


class CityPriceSerializer(serializers.Serializer):
    city = serializers.CharField()
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2)


class BaseProductSerializer(serializers.ModelSerializer):
    """Сериализатор базового продукта.
    Этот сериализатор предоставляет базовую функциональность для сериализации продуктов,
    включая категорию и бренд, а также получение URL-адресов изображений продукта.
    """

    tag_prod = TagSerializer(many=True, read_only=True)
    price = serializers.SerializerMethodField()
    average_rating = serializers.FloatField(read_only=True)
    reviews_count = serializers.IntegerField(read_only=True)
    # price = CityPriceSerializer(many=True, read_only=True)
    discount_amount_p = serializers.DecimalField(
        read_only=True,
        max_digits=5,
        decimal_places=2,
    )
    discount_amount_c = serializers.DecimalField(
        read_only=True,
        max_digits=5,
        decimal_places=2,
    )

    def get_price(self, obj):
        # Получаем минимальные цены по городам для данного продукта
        city_prices = (
            Stock.objects.filter(product=obj)
            .values("warehouse__city")
            .annotate(min_price=Min("price"))
            .values("warehouse__city__name_city", "min_price")
        )

        return {
            item["warehouse__city__name_city"]: item["min_price"]
            for item in city_prices
        }

    def get_related_entity_ids(self, instance: Products, related_model) -> List[int]:
        all_related_entities = related_model.objects.filter(product=instance)
        return [entity.id for entity in all_related_entities]

    def get_specifications(self, instance: Products) -> List[str]:
        return self.get_related_entity_ids(instance, Specifications)

    def get_stocks(self, instance: Products) -> List[str]:
        return self.get_related_entity_ids(instance, Stock)

    def get_image_urls(self, instance: Products) -> List[str]:
        """Получает URL-адреса изображений продукта.

        Args:
            instance (_type_): Экземпляр продукта.

        Returns:
            List[str]: Список URL-адресов изображений продукта.
        """
        all_entity_image_product = instance.productimage_set.all()
        return [image.image.url for image in all_entity_image_product]

    def to_representation(self, instance: Products) -> dict:
        """Преобразует экземпляр продукта в представление JSON.

        Args:
            instance Экземпляр продукта.

        Returns:
            dict: Представление JSON продукта.
        """
        representation = super().to_representation(instance)
        representation["list_url_to_image"] = self.get_image_urls(instance)
        # del representation["related_product"]
        # representation["list_specifications"] = self.get_specifications(instance)
        # representation["list_stocks"] = self.get_stocks(instance)
        return representation


class RelatedProductsSerializer(BaseProductSerializer):
    class Meta:
        model = Products
        fields = (
            "id",
            "name_product",
            "additional_data",
        )


class ProductsListSerializer(BaseProductSerializer):
    class Meta:
        model = Products
        fields = "__all__"


class ProductsDetailSerializer(BaseProductSerializer):
    category = CategorySerializer(read_only=True)
    brand = BrandsSerializer(read_only=True)
    present = ProductsListSerializer(many=True)
    services = ServiceSerializer(many=True)

    class Meta:
        model = Products
        fields = "__all__"


class PrductsListIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = (
            "id",
            "slug",
        )


class PopulatesProductsSerializer(serializers.ModelSerializer):
    products = ProductsListSerializer(many=True)

    class Meta:
        model = PopulatesProducts
        fields = "__all__"
