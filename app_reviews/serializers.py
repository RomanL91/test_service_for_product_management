from rest_framework import serializers
from app_reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    jwt_token = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Review
        fields = (
            "id",
            "rating",
            "review",
            "user_id",
            "product",
            "jwt_token",
        )
        read_only_fields = ("moderation", "user_id")

    def create(self, validated_data):
        jwt_token = validated_data.pop(
            "jwt_token", None
        )  # Извлекаем jwt_token из validated_data
        instance = super().create(validated_data)  # Создаем объект Review

        # Дополнительная логика с jwt_token, если необходимо

        return instance
