from rest_framework import routers

from app_products.views import ProductsViewSet
from app_category.views import CategoryViewSet


router = routers.DefaultRouter()

router.register(r"products", ProductsViewSet)
router.register(r"category", CategoryViewSet)
