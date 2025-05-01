from django.urls import path
from django.views.decorators.cache import cache_page

from rest_framework.urlpatterns import format_suffix_patterns

from app_category.views import category_facets


urlpatterns = [
    path(
        "categories/<int:pk>/facets/",
        cache_page(60 * 15)(
            category_facets,
        ),
        name="category-facets",
    )
]

urlpatterns_cat_suff = format_suffix_patterns(urlpatterns)
