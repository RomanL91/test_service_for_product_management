from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns

from app_products.views import ProductsViewSet


products_list = ProductsViewSet.as_view(
    {
        "get": "list",
    }
)

products_detail = ProductsViewSet.as_view(
    {
        "get": "retrieve",
    }
)

filter_by_cat = ProductsViewSet.as_view(
    {
        "get": "filter_by_cat",
    }
)

slugs = ProductsViewSet.as_view(
    {
        "get": "slugs",
    }
)

urlpatterns = [
    re_path(r"^api/v1/products/lang/(?P<lang>\w+)/$", products_list),
    re_path(
        r"^api/v1/products/(?P<slug_prod>[-\w]+)/lang/(?P<lang>\w+)/$",
        products_detail,
    ),
    re_path(r"^api/v1/products/filter_by_cat/(?P<slug_cat>[-\w]+)/$", filter_by_cat),
    re_path(
        r"^api/v1/products/filter_by_cat/(?P<slug_cat>[-\w]+)/lang/(?P<lang>\w+)/$",
        filter_by_cat,
    ),
    re_path(r"^api/v1/products/all/slugs/$", slugs),
    re_path(r"^api/v1/products/(?P<slug_prod>[-\w]+)/(?P<ids>[\d,]+)/$", products_list),
    re_path(
        r"^api/v1/products/(?P<slug_prod>[-\w]+)/(?P<ids>[\d,]+)/lang/(?P<lang>\w+)/$",
        products_list,
    ),
]

urlpatterns_products_suff = format_suffix_patterns(urlpatterns)
