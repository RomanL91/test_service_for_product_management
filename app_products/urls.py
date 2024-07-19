from django.urls import re_path, path
from rest_framework.urlpatterns import format_suffix_patterns

from app_products.views import (
    ProductsViewSet,
    ProductFilterView,
    ExternalProductBulkCreateAPIView,
)


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

vendor_cods = ProductsViewSet.as_view(
    {
        "get": "vendor_cods",
    }
)

products_by_ids = ProductsViewSet.as_view(
    {
        "get": "get_products_by_ids",
    }
)

urlpatterns = [
    re_path(
        r"^api/v1/products/filter_by_cat/(?P<slug_cat>[-\w]+)/$",
        filter_by_cat,
    ),
    path(
        "api/v1/products/all/slugs/",
        slugs,
    ),
    path(
        "api/v1/products/all/vendor_cods/",
        vendor_cods,
    ),
    path(
        "api/v1/products/by_ids/<str:ids>/",
        products_by_ids,
        name="products-by-ids",
    ),
    path(
        "api/v1/products/set/filter",
        ProductFilterView.as_view(),
        name="product-filter",
    ),
    path(
        "api/v1/external_products/",
        ExternalProductBulkCreateAPIView.as_view(),
        name="external-products-bulk-create",
    ),
]

urlpatterns_products_suff = format_suffix_patterns(urlpatterns)
