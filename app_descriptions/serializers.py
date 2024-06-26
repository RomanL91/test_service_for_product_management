from rest_framework import serializers

from app_descriptions.models import ProductDescription


class ProductDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDescription
        fields = "__all__"
