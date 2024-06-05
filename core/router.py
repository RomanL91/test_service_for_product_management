from rest_framework import routers

from app_products.views import ProductViewSet
from app_category.views import CategoryViewSet, BrandViewSet


router = routers.DefaultRouter()

router.register(r"product", ProductViewSet)
router.register(r"category", CategoryViewSet)
router.register(r"brand", BrandViewSet)
