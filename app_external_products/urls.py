from django.urls import path
from .views import offers_endpoint

urlpatterns_external_prod = [
    path("", offers_endpoint, name="offers-endpoint"),
]
