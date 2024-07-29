from rest_framework import routers

from app_products.views import ProductsViewSet, PopulatesProductsViewSet
from app_category.views import CategoryViewSet
from app_sales_points.views import StocksViewSet
from app_specifications.views import SpecificationsViewSet
from app_blogs.views import BlogViewSet
from app_reviews.views import ReviewViewSet
from app_descriptions.views import ProductDescriptionViewSet
from app_brands.views import BrandsViewSet
from app_kaspi.views import (
    CustomerViewSet,
    OrderViewSet,
    ProductViewSet,
)


router = routers.DefaultRouter()

router.register(r"blog", BlogViewSet)
router.register(r"populates", PopulatesProductsViewSet)
router.register(r"products", ProductsViewSet)
router.register(r"category", CategoryViewSet)
router.register(r"stocks", StocksViewSet)
router.register(r"specif", SpecificationsViewSet)
router.register(r"reviews", ReviewViewSet, basename="review")
router.register(r"descrip", ProductDescriptionViewSet, basename="descrip")
router.register(r"brands", BrandsViewSet, basename="brands")
# Для работы с Каспи
router.register(r"customers", CustomerViewSet)
router.register(r"orders", OrderViewSet)
router.register(r"kaspi_products", ProductViewSet)
