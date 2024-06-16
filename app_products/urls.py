from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns

from app_products.views import ProductsViewSet


translate_products_list = ProductsViewSet.as_view(
    {
        "get": "lang",
    }
)
translate_products_detail = ProductsViewSet.as_view(
    {
        "get": "lang_",
    }
)

urlpatterns = [
    re_path(r"^api/v1/products/lang/(?P<lang>\w+)/$", translate_products_list),
    re_path(
        r"^api/v1/products/(?P<pk>\d+)/lang_/(?P<lang>\w+)/$", translate_products_detail
    ),
]

urlpatterns_products_suff = format_suffix_patterns(urlpatterns)
