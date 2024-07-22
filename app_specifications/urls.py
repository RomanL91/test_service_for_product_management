from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns

from app_specifications.views import SpecificationsViewSet


filter_by_prod = SpecificationsViewSet.as_view(
    {
        "get": "filter_by_prod",
    }
)
filter_by_cat = SpecificationsViewSet.as_view(
    {
        "get": "filter_by_cat",
    }
)
get_specif_configurations = SpecificationsViewSet.as_view(
    {
        "get": "get_specif_product_configurations",
    }
)

urlpatterns = [
    re_path(
        r"api/v1/specif/by_category/(?P<cat_pk>\d+)/$",
        filter_by_cat,
        name="specifications-by-category",
    ),
    re_path(
        r"^api/v1/specif/filter_by_prod/(?P<prod_pk>\d+)/$",
        filter_by_prod,
    ),
    re_path(
        r"^api/v1/specif/configurations/(?P<ids>[\d,]+)/$",
        get_specif_configurations,
        name="specifications-configurations",
    ),
]

urlpatterns_specif_suff = format_suffix_patterns(urlpatterns)
