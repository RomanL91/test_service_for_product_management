from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns

from app_reviews.views import ReviewViewSet


filter_by_prod = ReviewViewSet.as_view(
    {
        "get": "filter_by_prod",
    }
)

urlpatterns = [
    re_path(
        r"^api/v1/reviews/filter_by_prod/(?P<prod_pk>\d+)/$",
        filter_by_prod,
    ),
]

urlpatterns_review_suff = format_suffix_patterns(urlpatterns)
