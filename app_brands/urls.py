from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns

from app_brands.views import BrandsViewSet


filter_by_cat_id = BrandsViewSet.as_view(
    {
        "get": "filter_by_cat_id",
    }
)
filter_by_cat_slug = BrandsViewSet.as_view(
    {
        "get": "filter_by_cat_slug",
    }
)

urlpatterns = [
    re_path(
        r"api/v1/brands/by_category/id/(?P<cat_pk>\d+)/$",
        filter_by_cat_id,
        name="brands-by-category_id",
    ),
    re_path(
        r"api/v1/brands/by_category/slug/(?P<cat_slug>\w+)/$",
        filter_by_cat_slug,
        name="brands-by-category_slug",
    ),
]

urlpatterns_brands_suff = format_suffix_patterns(urlpatterns)
