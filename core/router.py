from rest_framework import routers

from app_products.views import ProductsViewSet
from app_category.views import CategoryViewSet
from app_sales_points.views import StocksViewSet
from app_specifications.views import SpecificationsViewSet


router = routers.DefaultRouter()

router.register(r"products", ProductsViewSet)
router.register(r"category", CategoryViewSet)
router.register(r"stocks", StocksViewSet)
router.register(r"specif", SpecificationsViewSet)
