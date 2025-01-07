from django.utils.timezone import now
from django.db.models import Prefetch, Q, Avg, Count, Sum

from app_reviews.models import Review
from app_manager_tags.models import Tag
from app_sales_points.models import Stock, Edges
from app_specifications.models import Specifications
from app_products.models import Products, ProductImage
from app_discounts.models import ProductDiscount, CategoryDiscount, BrandDiscount


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
        Добавляем аннотации рейтинга и количества отзывов, включая сами отзывы.
        """
        return queryset.annotate(
            avg_rating=Avg("reviews__rating", filter=Q(reviews__moderation=True)),
            reviews_count=Count(
                "reviews", filter=Q(reviews__moderation=True), distinct=True
            ),
        ).prefetch_related(
            Prefetch(
                "reviews",
                queryset=Review.objects.filter(moderation=True).order_by("-created_at"),
            )
        )

    # -------------------------------
    # Скидки
    # -------------------------------
    @staticmethod
    def with_product_discounts(queryset):
        """
        Предзагружаем скидки ProductDiscount, связанные через product_discounts (ManyToMany).
        Фильтруем только активные.
        """
        discount_qs = ProductDiscount.objects.filter(active=True)
        return queryset.prefetch_related(
            Prefetch(
                "product_discounts",
                queryset=discount_qs,
                to_attr="prefetched_product_discounts",
            )
        )

    @staticmethod
    def with_category_discounts(queryset):
        """
        Предзагружаем скидки CategoryDiscount, связанные с категорией товара (category_discounts).
        """
        discount_qs = CategoryDiscount.objects.filter(active=True)
        return queryset.prefetch_related(
            Prefetch(
                "category__category_discounts",
                queryset=discount_qs,
                to_attr="prefetched_category_discounts",
            )
        )

    @staticmethod
    def with_brand_discounts(queryset):
        """
        Предзагружаем скидки BrandDiscount, связанные с брендом товара (brand_discounts).
        """
        discount_qs = BrandDiscount.objects.filter(active=True)
        return queryset.prefetch_related(
            Prefetch(
                "brand__brand_discounts",
                queryset=discount_qs,
                to_attr="prefetched_brand_discounts",
            )
        )

    @staticmethod
    def with_all_discounts(queryset):
        """
        Объединяем все три вида скидок: product, category, brand.
        """
        queryset = ProductsQueryFactory.with_product_discounts(queryset)
        queryset = ProductsQueryFactory.with_category_discounts(queryset)
        queryset = ProductsQueryFactory.with_brand_discounts(queryset)
        return queryset

    @staticmethod
    def only_in_stock(queryset):
        """
        Оставляем в выборке только те товары, у которых
        суммарный остаток (stocks__quantity) > 0.
        """
        return queryset.annotate(total_quantity=Sum("stocks__quantity")).filter(
            total_quantity__gt=0
        )

    @staticmethod
    def only_with_images(queryset):
        """
        Фильтрует товары, у которых есть хотя бы одно изображение.
        """
        return queryset.filter(productimage__isnull=False).distinct()

    # На этом уровне можно организовать кеширование (использую пока уровне маршрутов)
    @staticmethod
    def get_all_details():
        """
        Финальный метод, объединяющий все варианты prefetch и аннотаций
        """
        base = ProductsQueryFactory.get_base_query()
        base = ProductsQueryFactory.with_tags(base)
        base = ProductsQueryFactory.with_all_discounts(base)
        base = ProductsQueryFactory.with_images(base)
        base = ProductsQueryFactory.with_specifications(base)
        base = ProductsQueryFactory.with_stocks(base)
        base = ProductsQueryFactory.with_category_edges(base)
        base = ProductsQueryFactory.with_brand_edges(base)
        base = ProductsQueryFactory.with_related_products(base)
        base = ProductsQueryFactory.with_configuration(base)
        base = ProductsQueryFactory.annotate_reviews(base)
        base = ProductsQueryFactory.only_in_stock(base)
        base = ProductsQueryFactory.only_with_images(base)
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
