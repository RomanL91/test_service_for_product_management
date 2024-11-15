from django.urls import path

from app_elastic.views import SearchCategories, SearchProducts


urlpatterns = [
    path("category/<str:query>/", SearchCategories.as_view()),
    path("product/<str:query>/", SearchProducts.as_view()),
]
