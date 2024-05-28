from rest_framework import viewsets

from app_products.models import Products

from app_products.serializers import ProductsSerializer

from rest_framework.response import Response

from rest_framework.decorators import action


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductsSerializer
