from rest_framework import viewsets

# from rest_framework.response import Response # not use

from app_descriptions.models import ProductDescription
from app_descriptions.serializers import ProductDescriptionSerializer

# from core.lang_utils import TranslateManager # not use


class ProductDescriptionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductDescription.objects.all()
    serializer_class = ProductDescriptionSerializer

    # not use
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.translate_manager = TranslateManager(self)

    # def filter_by_prod(self, request, prod_pk, *args, **kwargs):
    #     specif = ProductDescription.objects.filter(product_id=prod_pk)
    #     serializer = self.get_serializer(specif, many=True)
    #     return Response(serializer.data)
