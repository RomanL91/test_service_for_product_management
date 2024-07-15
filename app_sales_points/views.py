from rest_framework import viewsets
from rest_framework.response import Response

from app_sales_points.models import Stock
from app_sales_points.serializers import StockSerializer


class StocksViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer

    def filter_by_prod(self, request, prod_pk, city_pk=None, *args, **kwargs):
        stocks = Stock.objects.filter(product_id=prod_pk, warehouse__city=city_pk)
        serializer = self.get_serializer(stocks, many=True)
        return Response(serializer.data)
