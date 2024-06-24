from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns

from app_specifications.views import SpecificationsViewSet


filter_by_prod = SpecificationsViewSet.as_view(
    {
        "get": "filter_by_prod",
    }
)

urlpatterns = [
    re_path(
        r"^api/v1/specif/filter_by_prod/(?P<prod_pk>\d+)/$",
        filter_by_prod,
    ),
    re_path(
        r"^api/v1/specif/filter_by_prod/(?P<prod_pk>\d+)/lang/(?P<lang>\w+)/$",
        filter_by_prod,
    ),
]

urlpatterns_specif_suff = format_suffix_patterns(urlpatterns)
