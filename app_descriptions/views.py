from rest_framework import viewsets

from rest_framework.response import Response

from app_descriptions.models import ProductDescription
from app_descriptions.serializers import ProductDescriptionSerializer


class ProductDescriptionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductDescription.objects.all()
    serializer_class = ProductDescriptionSerializer

    def filter_by_prod(self, request, prod_pk, *args, **kwargs):
        specif = ProductDescription.objects.filter(id=prod_pk)
        serializer = self.get_serializer(specif, many=True)
        return Response(serializer.data)
