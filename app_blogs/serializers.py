from rest_framework import serializers

from app_blogs.models import Blog, BlogImage

from app_products.serializers import ProductsListSerializer


class BlogImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogImage
        fields = ("image",)


class BlogSerializer(serializers.ModelSerializer):
    related_product = ProductsListSerializer(many=True)
    images = BlogImageSerializer(
        source="blogimage_set",
        many=True,
        read_only=True,
    )

    class Meta:
        model = Blog
        fields = "__all__"
