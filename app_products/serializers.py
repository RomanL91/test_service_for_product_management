from typing import List
from rest_framework import serializers

from app_products.models import Products, ProductImage

from app_category.serializers import CategorySerializer
from app_brands.serializers import BrandsSerializer
from app_specifications.serializers import SpecificationsSerializer


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = "__all__"


class BaseProductSerializer(serializers.ModelSerializer):
    """Сериализатор базового продукта.
    Этот сериализатор предоставляет базовую функциональность для сериализации продуктов,
    включая категорию и бренд, а также получение URL-адресов изображений продукта.
    """

    def get_specifications(self, instance: Products) -> List[str]:
        all_entity_specifications_product = instance.specifications_set.all()
        return [SpecificationsSerializer(entity).data for entity in all_entity_specifications_product]

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
        representation["list_specifications"] = self.get_specifications(instance)
        return representation


class RelatedProductsSerializer(BaseProductSerializer):
    class Meta:
        model = Products
        fields = "__all__"

    def to_representation(self, instance: Products) -> dict:
        representation = super().to_representation(instance)
        del representation["related_product"]
        del representation["category"]
        del representation["brand"]
        return representation


class ProductsListSerializer(BaseProductSerializer):

    class Meta:
        model = Products
        fields = "__all__"


class ProductsDetailSerializer(BaseProductSerializer):
    category = CategorySerializer(read_only=True)
    related_product = RelatedProductsSerializer(many=True, read_only=True)
    brand = BrandsSerializer(read_only=True)

    class Meta:
        model = Products
        fields = "__all__"
