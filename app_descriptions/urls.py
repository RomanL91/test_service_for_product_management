from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns

from app_descriptions.views import ProductDescriptionViewSet


filter_by_prod = ProductDescriptionViewSet.as_view(
    {
        "get": "filter_by_prod",
    }
)

urlpatterns = [
    re_path(
        r"^api/v1/descrip/filter_by_prod/(?P<prod_pk>\d+)/$",
        filter_by_prod,
        name="all_desc_to_product",
    ),
]

urlpatterns_descrip_suff = format_suffix_patterns(urlpatterns)
