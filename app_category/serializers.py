from typing import List

from rest_framework import serializers

from app_category.models import Category


class CategorySerializer(serializers.ModelSerializer):
    visible_products_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = "__all__"

    def get_image_urls(self, instance: Category, related_set_name: str) -> List[str]:
        related_set = getattr(instance, related_set_name).all()
        return [image.image.url for image in related_set if image.image]

    def get_image_category_urls(self, instance: Category) -> List[str]:
        return self.get_image_urls(instance, "categoryimage_set")

    def get_image_banner_urls(self, instance: Category) -> List[str]:
        return self.get_image_urls(instance, "bannerimage_set")

    def to_representation(self, instance: Category) -> dict:
        representation = super().to_representation(instance)
        representation["list_url_to_image"] = self.get_image_category_urls(instance)
        representation["list_url_to_baner"] = self.get_image_banner_urls(instance)
        return representation


class CategorySerializerElastic(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name_category",
            "slug",
            "additional_data",
        ]
