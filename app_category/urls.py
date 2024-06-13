from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns

from app_category.views import CategoryViewSet


translate_category_list = CategoryViewSet.as_view({"get": "lang"})

translate_category_detail = CategoryViewSet.as_view(
    {
        "get": "lang_",
    }
)

translation_products_category = CategoryViewSet.as_view(
    {
        "get": "products",
    }
)


urlpatterns = [
    re_path(r"^api/v1/category/lang/(?P<lang>\w+)/$", translate_category_list),
    re_path(
        r"^api/v1/category/(?P<pk>\d+)/lang_/(?P<lang>\w+)/$", translate_category_detail
    ),
    re_path(
        r"^api/v1/category/(?P<pk>\d+)/products/(?P<lang>\w+)/$",
        translation_products_category,
    ),
]

urlpatterns_category_suff = format_suffix_patterns(urlpatterns)
