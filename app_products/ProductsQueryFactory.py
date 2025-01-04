from django.utils.timezone import now
from django.db.models import Prefetch, Avg, Count

from app_manager_tags.models import Tag
from app_sales_points.models import Stock, Edges
from app_specifications.models import Specifications
from app_products.models import Products, ProductImage


class ProductsQueryFactory:
    """
    Фабрика для создания различных вариантов QuerySet для Products.
    """

    @staticmethod
    def get_base_query():
        """
        Базовый QuerySet без сложных prefetch/annotate, но с select_related
        """
        return Products.objects.select_related("category__parent", "brand")

    @staticmethod
    def with_tags(queryset, to_attr="prefetched_tags"):
        """
        Добавляем prefetch_related для тегов
        """
        return queryset.prefetch_related(
            Prefetch(
                "tag_prod",
                queryset=Tag.objects.only(
                    "id", "tag_text", "font_color", "fill_color", "additional_data"
                ),
                to_attr=to_attr,
            )
        )

    @staticmethod
    def with_images(queryset, to_attr="images"):
        """
        Добавляем prefetch_related для изображений
        """
        return queryset.prefetch_related(
            Prefetch(
                "productimage_set",
                queryset=ProductImage.objects.select_related("product"),
                to_attr=to_attr,
            )
        )

    @staticmethod
    def with_specifications(queryset, to_attr="prefetched_specifications"):
        """
        Добавляем prefetch_related для спецификаций
        """
        return queryset.prefetch_related(
            Prefetch(
                "specifications",
                queryset=Specifications.objects.select_related(
                    "name_specification", "value_specification"
                ),
                to_attr=to_attr,
            )
        )

    @staticmethod
    def with_stocks(queryset, to_attr="prefetched_stocks"):
        """
        Добавляем prefetch_related для остатков
        """
        return queryset.prefetch_related(
            Prefetch(
                "stocks",
                queryset=Stock.objects.select_related("warehouse__city"),
                to_attr=to_attr,
            )
        )

    @staticmethod
    def with_category_edges(queryset, to_attr="related_edges"):
        """
        Добавляем prefetch_related для ребер категории
        """
        return queryset.prefetch_related(
            Prefetch(
                "category__edges",
                queryset=Edges.objects.filter(
                    expiration_date__gt=now(), is_active=True
                ).select_related("city_from", "city_to"),
                to_attr=to_attr,
            )
        )

    @staticmethod
    def with_brand_edges(queryset, to_attr="related_edges"):
        """
        Добавляем prefetch_related для ребер бренда
        """
        return queryset.prefetch_related(
            Prefetch(
                "brand__edges",
                queryset=Edges.objects.filter(
                    expiration_date__gt=now(), is_active=True
                ).select_related("city_from", "city_to"),
                to_attr=to_attr,
            )
        )

    @staticmethod
    def with_related_products(queryset, to_attr="prefetched_related_products"):
        """
        Добавляем prefetch_related для связанных продуктов (related_product)
        """
        # Собираем подзапрос для связанных продуктов
        related_qs = Products.objects.prefetch_related(
            Prefetch(
                "stocks",
                queryset=Stock.objects.select_related("warehouse__city"),
                to_attr="prefetched_stocks",
            ),
            Prefetch(
                "tag_prod",
                queryset=Tag.objects.only("id", "tag_text", "font_color", "fill_color"),
                to_attr="prefetched_tags",
            ),
            Prefetch(
                "productimage_set",
                queryset=ProductImage.objects.select_related("product"),
                to_attr="images",
            ),
        ).select_related("category", "brand")

        return queryset.prefetch_related(
            Prefetch("related_product", queryset=related_qs, to_attr=to_attr)
        )

    @staticmethod
    def with_configuration(queryset, to_attr="prefetched_configuration"):
        """
        Добавляем prefetch_related для комплектаций (configuration)
        """
        config_qs = Products.objects.prefetch_related(
            Prefetch(
                "tag_prod",
                queryset=Tag.objects.only("id", "tag_text", "font_color", "fill_color"),
                to_attr="prefetched_tags",
            ),
            Prefetch(
                "productimage_set",
                queryset=ProductImage.objects.select_related("product"),
                to_attr="images",
            ),
        )
        return queryset.prefetch_related(
            Prefetch("configuration", queryset=config_qs, to_attr=to_attr)
        )

    @staticmethod
    def annotate_reviews(queryset):
        """
        Добавляем аннотации рейтинга и количества отзывов
        """
        return queryset.annotate(
            avg_rating=Avg("review__rating"),
            reviews_count=Count("review", distinct=True),
        )

    # На этом уровне можно организовать кеширование (использую пока уровне маршрутов)
    @staticmethod
    def get_all_details():
        """
        Финальный метод, объединяющий все варианты prefetch и аннотаций
        """
        base = ProductsQueryFactory.get_base_query()
        base = ProductsQueryFactory.with_tags(base)
        base = ProductsQueryFactory.with_images(base)
        base = ProductsQueryFactory.with_specifications(base)
        base = ProductsQueryFactory.with_stocks(base)
        base = ProductsQueryFactory.with_category_edges(base)
        base = ProductsQueryFactory.with_brand_edges(base)
        base = ProductsQueryFactory.with_related_products(base)
        base = ProductsQueryFactory.with_configuration(base)
        base = ProductsQueryFactory.annotate_reviews(base)
        return base

    @staticmethod
    def get_list_view():  # После добавления кеширования, больше не использую этот метод
        """
        Возвращает QuerySet, который подгружает
        только минимум данных, необходимых для списка товаров.
        """
        base = ProductsQueryFactory.get_base_query()
        base = ProductsQueryFactory.with_tags(base)
        base = ProductsQueryFactory.with_images(base)
        base = ProductsQueryFactory.with_stocks(base)
        base = ProductsQueryFactory.annotate_reviews(base)
        # Опционально можно дополнить категориями или брендами, если нужно
        return base
