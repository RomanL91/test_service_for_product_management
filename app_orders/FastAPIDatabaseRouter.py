class FastAPIDatabaseRouter:
    """
    A router to control all database operations for models related to the FastAPI database.
    """

    def db_for_read(self, model, **hints):
        """Directs read operations to the FastAPI database for specific models."""
        if (
            model._meta.app_label != "app_orders"
        ):  # User и другие стандартные модели Django
            return "default"
        if model._meta.app_label == "app_orders":  # Укажите ваше приложение
            return "fastapi_db"
        return None

    def db_for_write(self, model, **hints):
        """Directs write operations to the FastAPI database for specific models."""
        if (
            model._meta.app_label != "app_orders"
        ):  # User и другие стандартные модели Django
            return "default"
        if model._meta.app_label == "app_orders":  # Укажите ваше приложение
            return "fastapi_db"
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations if models are in the same database."""
        db_set = {"fastapi_db", "default"}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ensure that migrations only occur for the relevant database."""
        if app_label == "app_orders":
            return db == "fastapi_db"
        return db == "default"
