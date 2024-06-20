from rest_framework import routers

from app_products.views import ProductsViewSet
from app_category.views import CategoryViewSet
from app_sales_points.views import StocksViewSet


router = routers.DefaultRouter()

router.register(r"products", ProductsViewSet)
router.register(r"category", CategoryViewSet)
router.register(r"stocks", StocksViewSet)
