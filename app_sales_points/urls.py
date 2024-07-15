from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns

from app_sales_points.views import StocksViewSet


filter_by_prod = StocksViewSet.as_view(
    {
        "get": "filter_by_prod",
    }
)
get_prices_by_category = StocksViewSet.as_view(
    {
        "get": "get_prices_by_category",
    }
)

urlpatterns = [
    re_path(
        r"^api/v1/stocks/filter_by_prod/(?P<prod_pk>\d+)/(?P<city_pk>\d+)/$",
        filter_by_prod,
    ),
    re_path(
        r"^api/v1/stocks/prices_by_category/(?P<cat_pk>\d+)/$",
        get_prices_by_category,
    ),
]

urlpatterns_stocks_suff = format_suffix_patterns(urlpatterns)
