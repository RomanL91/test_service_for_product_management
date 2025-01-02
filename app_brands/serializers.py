from rest_framework import serializers

from app_brands.models import Brands


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brands
        fields = [
            "id",
            "name_brand",
            "additional_data",
        ]
