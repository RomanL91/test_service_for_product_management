from rest_framework import serializers

from app_brands.models import Brands, LogoBrand


class LogoBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogoBrand
        fields = ["image"]


class BrandSerializer(serializers.ModelSerializer):
    logo = LogoBrandSerializer(
        many=True,
        read_only=True,
        source="logobrand_set",
    )

    class Meta:
        model = Brands
        fields = [
            "id",
            "name_brand",
            "additional_data",
            "logo",
        ]
