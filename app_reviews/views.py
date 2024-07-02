import jwt

from rest_framework import viewsets, status
from rest_framework.response import Response

from django.conf import settings
from app_reviews.models import Review
from app_reviews.serializers import ReviewSerializer


# TODO Переправить варианты ответов, меньше информации клиенту - выше защита
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    http_method_names = [
        "get",
        "post",
    ]

    def create(self, request):
        jwt_token = request.data.get("jwt_token")

        if not jwt_token:
            return Response(
                {
                    "error": "JWT token is required",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Декодирование и валидация JWT токена
            payload = jwt.decode(
                jwt_token,
                settings.SIMPLE_JWT["VERIFYING_KEY"],
                algorithms=[settings.SIMPLE_JWT["ALGORITHM"]],
            )
            user_id = payload["user_id"]
            token_type = payload["type"]
            if token_type != "access":  # если не access
                raise jwt.InvalidTokenError()
        except jwt.ExpiredSignatureError as e:
            return Response(
                {"error": f"JWT token has expired: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except jwt.InvalidTokenError as e:
            return Response(
                {"error": f"Invalid JWT token: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except jwt.PyJWTError as e:
            return Response(
                {"error": f"Error decoding JWT token: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except KeyError:
            raise jwt.InvalidTokenError()

        # Создание отзыва
        serializer = ReviewSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user_id=user_id)
            return Response(
                {
                    "message": "Отзыв успешно создан",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def filter_by_prod(self, request, prod_pk, *args, **kwargs):
        specif = Review.objects.filter(product_id=prod_pk)
        serializer = self.get_serializer(specif, many=True)
        return Response(serializer.data)
