from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns

from app_category.views import CategoryViewSet


translate_category_list = CategoryViewSet.as_view(
    {
        "get": "lang",
    }
)
category_detail = CategoryViewSet.as_view(
    {
        "get": "retrieve",
    }
)
translate_category_detail = CategoryViewSet.as_view(
    {
        "get": "lang_",
    }
)


urlpatterns = [
    re_path(r"^api/v1/category/lang/(?P<lang>\w+)/$", translate_category_list),
    re_path(r"^api/v1/category/(?P<slug_cat>[-\w]+)/$", category_detail),
    re_path(
        r"^api/v1/category/(?P<slug_cat>[-\w]+)/lang_/(?P<lang>\w+)/$",
        translate_category_detail,
    ),
]

urlpatterns_category_suff = format_suffix_patterns(urlpatterns)
