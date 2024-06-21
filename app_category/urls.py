from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns

from app_category.views import CategoryViewSet


translate_category_list = CategoryViewSet.as_view(
    {
        "get": "list",
    }
)
translate_category_detail = CategoryViewSet.as_view(
    {
        "get": "retrieve",
    }
)

urlpatterns = [
    re_path(r"^api/v1/category/lang/(?P<lang>\w+)/$", translate_category_list),
    re_path(
        r"^api/v1/category/(?P<slug_cat>[-\w]+)/lang/(?P<lang>\w+)/$",
        translate_category_detail,
    ),
]

urlpatterns_category_suff = format_suffix_patterns(urlpatterns)
