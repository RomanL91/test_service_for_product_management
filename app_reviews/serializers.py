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
            "user_uuid",
            "product",
            "jwt_token",
        )
        read_only_fields = ("moderation", "user_uuid")

    def create(self, validated_data):
        print(f"--- serializers --- validated_data --- {validated_data}")

        jwt_token = validated_data.pop(
            "jwt_token", None
        )  # Извлекаем jwt_token из validated_data
        print(f"--- serializers --- jwt_token --- {jwt_token}")
        instance = super().create(validated_data)  # Создаем объект Review
        print(f"--- serializers --- instance --- {instance}")

        # Дополнительная логика с jwt_token, если необходимо

        return instance


class ReviewsForProductsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = (
            "id",
            "rating",
            "review",
            "created_at",
        )
