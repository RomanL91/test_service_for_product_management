from typing import List
from rest_framework import serializers
from app_products.models import Products, ProductImage
from app_category.serializers import CategorySerializer


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = "__all__"


class BaseProductSerializer(serializers.ModelSerializer):
    """Сериализатор базового продукта.
    Этот сериализатор предоставляет базовую функциональность для сериализации продуктов,
    включая категорию и бренд, а также получение URL-адресов изображений продукта.


    Args:
        category (CategorySerializer): Сериализатор категории продукта.
        brand (BrandSerializer): Сериализатор бренда продукта.
    """

    # category = CategorySerializer() # TODO думаю это не нужно в выводе списка

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
        return representation


class RelatedProductsSerializer(BaseProductSerializer):
    class Meta:
        model = Products
        fields = "__all__"

    def to_representation(self, instance: Products) -> dict:
        representation = super().to_representation(instance)
        del representation["related_products"]
        return representation


class ProductsSerializer(BaseProductSerializer):
    related_products = RelatedProductsSerializer(many=True, read_only=True)

    class Meta:
        model = Products
        fields = "__all__"
