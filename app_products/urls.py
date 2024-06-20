from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns

from app_products.views import ProductsViewSet


translate_products_list = ProductsViewSet.as_view(
    {
        "get": "lang",
    }
)
product_detail = ProductsViewSet.as_view(
    {
        "get": "retrieve",
    }
)
translate_products_detail = ProductsViewSet.as_view(
    {
        "get": "lang_",
    }
)

filter_by_cat = ProductsViewSet.as_view(
    {
        "get": "filter_by_cat",
    }
)
translate_products_filter_by_cat = ProductsViewSet.as_view(
    {
        "get": "lang",
    }
)
ids = ProductsViewSet.as_view(
    {
        "get": "ids",
    }
)


urlpatterns = [
    re_path(r"^api/v1/products/lang/(?P<lang>\w+)/$", translate_products_list),
    re_path(r"^api/v1/products/(?P<slug_prod>[-\w]+)/$", product_detail),
    re_path(
        r"^api/v1/products/(?P<slug_prod>[-\w]+)/lang_/(?P<lang>\w+)/$",
        translate_products_detail,
    ),
    re_path(r"^api/v1/products/filter_by_cat/(?P<slug_cat>[-\w]+)/$", filter_by_cat),
    re_path(
        r"^api/v1/products/filter_by_cat/(?P<slug_cat>[-\w]+)/lang/(?P<lang>\w+)/$",
        translate_products_filter_by_cat,
    ),
    re_path(r"^api/v1/products/all/ids/$", ids),
]

urlpatterns_products_suff = format_suffix_patterns(urlpatterns)
