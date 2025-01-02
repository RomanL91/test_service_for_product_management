from django.contrib import admin
from django.urls import path, include

from django.conf.urls.static import static
from django.conf import settings

from .router import router

from app_category.urls import urlpatterns_category_suff
from app_products.urls import urlpatterns_products_suff
from app_sales_points.urls import urlpatterns_stocks_suff
from app_specifications.urls import urlpatterns_specif_suff
from app_reviews.urls import urlpatterns_review_suff

from app_descriptions.urls import urlpatterns_descrip_suff
from app_brands.urls import urlpatterns_brands_suff
from app_orders.urls import urlpatterns as url_orders_api

# api v2
from app_products.urls_v2 import urlpatterns as urlpatterns_products_v2

urlpatterns = (
    [
        path("admin/", admin.site.urls),
        path("api/v1/", include(router.urls)),
        path("api/v2/", include(urlpatterns_products_v2)),
        path("api/orders/", include(url_orders_api)),
        path("search/", include("app_elastic.urls")),
        path("silk/", include("silk.urls", namespace="silk")),
    ]
    + urlpatterns_category_suff
    + urlpatterns_products_suff
    + urlpatterns_stocks_suff
    + urlpatterns_specif_suff
    + urlpatterns_review_suff
    + urlpatterns_descrip_suff
    + urlpatterns_brands_suff
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)


admin.site.site_header = "Администрирование Магазина"
admin.site.index_title = "Администрирование Магазина"  # default: "Site administration"
admin.site.site_title = "Администрирование Магазина"  # default: "Django site admin"
admin.site.site_url = None
# admin.site.disable_action('delete_selected')
