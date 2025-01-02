from rest_framework import serializers

from app_category.models import Category


class CategorySerializer(serializers.ModelSerializer):
    parent_category_name = serializers.CharField(
        source="parent.name_category", read_only=True
    )

    class Meta:
        model = Category
        fields = [
            "id",
            "name_category",
            "slug",
            "parent",
            "parent_category_name",
            "additional_data",
        ]
