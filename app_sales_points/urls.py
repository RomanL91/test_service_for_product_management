from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns

from app_sales_points.views import StocksViewSet

translate_stocks_list = StocksViewSet.as_view(
    {
        "get": "lang",
    }
)
filter_by_prod = StocksViewSet.as_view(
    {
        "get": "filter_by_prod",
    }
)
translate_stocks_filter_by_prod = StocksViewSet.as_view(
    {
        "get": "lang",
    }
)


urlpatterns = [
    re_path(r"^api/v1/stocks/lang/(?P<lang>\w+)/$", translate_stocks_list),
    re_path(r"^api/v1/stocks/filter_by_prod/(?P<slug_prod>[-\w]+)/$", filter_by_prod),
    re_path(
        r"^api/v1/stocks/filter_by_prod/(?P<slug_prod>[-\w]+)/lang/(?P<lang>\w+)/$",
        translate_stocks_filter_by_prod,
    ),
]

urlpatterns_stocks_suff = format_suffix_patterns(urlpatterns)
