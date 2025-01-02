from rest_framework.routers import DefaultRouter
from app_products.views_v2 import ProductsViewSet_v2

router = DefaultRouter()
router.register(r"products_v2", ProductsViewSet_v2, basename="product_v2")

urlpatterns = [
    # Другие маршруты
    *router.urls,
]
