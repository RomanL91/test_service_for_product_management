from django.urls import path
from django.views.decorators.cache import cache_page
from app_products.views_v2 import ProductsViewSet_v2
from app_products.SmartGlobalSearch import SmartGlobalSearchView


urlpatterns = [
    path(
        "globalsearch/",
        # cache_page(60 * 15)(
        SmartGlobalSearchView.as_view(),
        # ),
        name="products-list",
    ),
    path(
        "products_v2/",
        cache_page(60 * 15)(
            ProductsViewSet_v2.as_view({"get": "list"}),
        ),
        name="products-list",
    ),
    path(
        "products_v2/details/<slug:slug>/",
        cache_page(60 * 15)(
            ProductsViewSet_v2.as_view({"get": "retrieve"}),
        ),
        name="products-detail",
    ),
    path(
        "products_v2/filter_by_ids/",
        cache_page(60 * 15)(
            ProductsViewSet_v2.as_view({"get": "filter_by_ids"}),
        ),
        name="products-filter-by-ids",
    ),
    path(
        "products_v2/popular_set/",
        cache_page(60 * 15)(
            ProductsViewSet_v2.as_view({"get": "popular_set"}),
        ),
        name="popular-set-products",
    ),
    path(
        "products_v2/category/<slug:category_slug>/",
        cache_page(60 * 15)(
            ProductsViewSet_v2.as_view({"get": "products_by_category"}),
        ),
        name="products-by-category",
    ),
    path(
        "products_v2/filter_by_city/",
        cache_page(60 * 15)(
            ProductsViewSet_v2.as_view({"get": "filter_by_city"}),
        ),
        name="filter-by-city",
    ),
    path(
        "products_v2/discounted/",
        cache_page(60 * 15)(
            ProductsViewSet_v2.as_view({"get": "discounted"}),
        ),
        name="discounted",
    ),
]
