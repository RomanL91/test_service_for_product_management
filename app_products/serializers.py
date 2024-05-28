from rest_framework import serializers

from app_products.models import Products

from app_category.serializers import CategorySerializer, BrandSerializer


class ProductsSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    brand = BrandSerializer()

    class Meta:
        model = Products
        fields = "__all__"
