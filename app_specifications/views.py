from rest_framework import viewsets
from rest_framework.response import Response

from app_specifications.models import Specifications
from app_specifications.serializers import SpecificationsSerializer


class SpecificationsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Specifications.objects.all()
    serializer_class = SpecificationsSerializer

    def filter_by_prod(self, request, prod_pk, *args, **kwargs):
        specif = Specifications.objects.filter(product_id=prod_pk)
        serializer = self.get_serializer(specif, many=True)
        return Response(serializer.data)
