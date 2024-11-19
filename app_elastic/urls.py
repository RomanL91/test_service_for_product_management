from django.urls import path

from app_elastic.views import SearchCategories, SearchProducts, FilterProducts


urlpatterns = [
    path("category/<str:query>/", SearchCategories.as_view()),
    path("product/<str:query>/", SearchProducts.as_view()),
    path("filter_products/", FilterProducts.as_view()),
]
