from rest_framework import routers

from app_products.views import ProductsViewSet, PopulatesProductsViewSet
from app_category.views import CategoryViewSet
from app_sales_points.views import StocksViewSet
from app_specifications.views import SpecificationsViewSet
from app_blogs.views import BlogViewSet


router = routers.DefaultRouter()

router.register(r"blog", BlogViewSet)
router.register(r"populates", PopulatesProductsViewSet)
router.register(r"products", ProductsViewSet)
router.register(r"category", CategoryViewSet)
router.register(r"stocks", StocksViewSet)
router.register(r"specif", SpecificationsViewSet)
