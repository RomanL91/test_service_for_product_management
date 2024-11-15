from django.urls import path

from app_elastic.views import SearchCategories, SearchProducts


urlpatterns = [
    path("category_s/<str:query>/", SearchCategories.as_view()),
    path("product_s/<str:query>/", SearchProducts.as_view()),
]
