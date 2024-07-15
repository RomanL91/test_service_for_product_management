from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns

from app_category.views import CategoryViewSet


subcategories_list = CategoryViewSet.as_view(
    {
        "get": "subcategories",
    }
)


urlpatterns = [
    re_path(
        r"^api/v1/category/(?P<slug_cat>[-\w]+)/subcategories/$",
        subcategories_list,
    ),
]

urlpatterns_category_suff = format_suffix_patterns(urlpatterns)
