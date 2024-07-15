from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns

from app_brands.views import BrandsViewSet


filter_by_cat = BrandsViewSet.as_view(
    {
        "get": "filter_by_cat",
    }
)

urlpatterns = [
    re_path(
        r"api/v1/brands/by_category/(?P<cat_pk>\d+)/$",
        filter_by_cat,
        name="brands-by-category",
    ),
]

urlpatterns_brands_suff = format_suffix_patterns(urlpatterns)
