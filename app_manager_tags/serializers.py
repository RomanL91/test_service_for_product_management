from rest_framework import serializers

from app_manager_tags.models import Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = [
            "id",
            "tag_text",
            "font_color",
            "fill_color",
            "additional_data",
        ]
