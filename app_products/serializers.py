from rest_framework import serializers

from app_products.models import Products, ProductImage

from app_category.serializers import CategorySerializer, BrandSerializer


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = "__all__"


class ProductsSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    brand = BrandSerializer()

    class Meta:
        model = Products
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        all_entity_image_product = instance.productimage_set.all()
        list_url_to_image = [image.image.url for image in all_entity_image_product]
        representation["list_url_to_image"] = list_url_to_image

        return representation
