from django.urls import path
from django.views.decorators.cache import cache_page
from app_products.views_v2 import ProductsViewSet_v2


urlpatterns = [
    # path(
    #     "products_v2/",
    #     cache_page(60 * 15)(ProductsViewSet_v2.as_view({"get": "list"})),
    #     name="products-list",
    # ),
    # path(
    #     "products_v2/details/<slug:slug>/",
    #     cache_page(60 * 15)(ProductsViewSet_v2.as_view({"get": "retrieve"})),
    #     name="products-detail",
    # ),
    path(
        "products_v2/",
        ProductsViewSet_v2.as_view({"get": "list"}),
        name="products-list",
    ),
    path(
        "products_v2/details/<slug:slug>/",
        ProductsViewSet_v2.as_view({"get": "retrieve"}),
        name="products-detail",
    ),
    path(
        "products_v2/filter_by_ids/",
        ProductsViewSet_v2.as_view({"get": "filter_by_ids"}),
        name="products-filter-by-ids",
    ),
]
