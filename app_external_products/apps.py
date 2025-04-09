from django.apps import AppConfig


class AppExternalProductsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app_external_products"

    def ready(self):
        from app_external_products import signals
