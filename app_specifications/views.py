from rest_framework import viewsets
from rest_framework.response import Response

from app_specifications.models import Specifications
from app_specifications.serializers import SpecificationsSerializer

from core.lang_utils import TranslateManager


class SpecificationsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Specifications.objects.all()
    serializer_class = SpecificationsSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.translate_manager = TranslateManager(self)

    def filter_by_prod(self, request, prod_pk, lang=None, *args, **kwargs):
        specif = Specifications.objects.filter(product_id=prod_pk)
        serializer = self.get_serializer(specif, many=True)
        if lang is not None:
            self.translate_manager.translate_nested_fields(
                serializer.data, ["name_specification", "value_specification"], lang
            )
        return Response(serializer.data)
