from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response

from app_category.models import Category
from app_category.serializers import CategorySerializer
from app_products.ProductsQueryFactory import ProductsQueryFactory
from app_products.views_v2 import (
    ProductsViewSet_v2,
)

from rest_framework.decorators import action
from app_brands.models import Brands
from app_brands.serializers import BrandSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Пример CategoryViewSet, который показывает только те категории,
    у которых есть хотя бы один товар, «видимый» для запрошенного города.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"

    def list(self, request, *args, **kwargs):
        """
        GET /categories/?city=НазваниеГорода
        Возвращает «прореженное» дерево категорий, в которых есть
        хотя бы один товар, доступный (через остатки или рёбра) для данного города.
        """
        city_name = request.query_params.get("city")
        if city_name:
            # 1) Собираем «видимые» для города товары
            products_qs = ProductsQueryFactory.get_all_details()
            products_qs = ProductsViewSet_v2.filter_by_city_and_edges(
                self=None,  # Потому что метод filter_by_city_and_edges — статический по смыслу
                queryset=products_qs,
                city_name=city_name,
            )

            # 2) Определяем список категорий, в которых есть «видимый» товар
            category_ids_with_products = products_qs.values_list(
                "category_id", flat=True
            ).distinct()

            # 3) Расширяем за счёт всех ancestor'ов:
            #    если у подкатегории есть видимые товары, её родитель тоже нужен в дереве.
            all_category_ids = set(category_ids_with_products)
            for cat_id in category_ids_with_products:
                ancestors = Category.objects.get(id=cat_id).get_ancestors()
                all_category_ids.update(a.id for a in ancestors)

            # 4) Достаём все нужные категории из базы
            #    и АННОТИРУЕМ счётчик видимых продуктов (чтобы при сборке дерева знать, где 0)
            categories_qs = Category.objects.filter(id__in=all_category_ids).annotate(
                visible_products_count=Count(
                    "products",
                    filter=Q(products__in=products_qs),
                    distinct=True,
                )
            )
        else:
            # Если город не задан, возвращаем всё как обычно (или оставьте пустой список — на ваше усмотрение)
            categories_qs = self.filter_queryset(
                self.get_queryset().annotate(visible_products_count=Count("products"))
            )

        # Превращаем в serializer.data
        serializer = self.get_serializer(categories_qs, many=True)

        # 5) Собираем дерево
        tree = self.build_tree(serializer.data)

        # 6) «Прореживаем» пустые категории
        pruned_tree = [node for node in tree if self.prune_empty(node)]

        return Response(pruned_tree)

    def retrieve(self, request, slug=None, *args, **kwargs):
        instance = self.get_object_by_slug(slug)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_object_by_slug(self, slug):
        return get_object_or_404(self.get_queryset(), slug=slug)

    def build_tree(self, categories):
        """
        Собирает дерево категорий, как в вашем исходном коде.
        Но теперь у нас есть поле 'visible_products_count'.
        """
        category_map = {}
        roots = []

        for cat in categories:
            cat["children"] = []
            category_map[cat["id"]] = cat

        for cat in categories:
            parent_id = cat["parent"]
            if parent_id is None:
                roots.append(cat)
            else:
                category_map[parent_id]["children"].append(cat)

        return roots

    def prune_empty(self, node):
        """
        Рекурсивно исключаем узлы, у которых visible_products_count == 0
        и нет детей с товарами.
        """
        # Сначала обрабатываем детей
        node["children"] = [
            child for child in node["children"] if self.prune_empty(child)
        ]

        # Если нет видимых товаров и нет детей — узел "мертв"
        if node.get("visible_products_count", 0) == 0 and not node["children"]:
            return False
        return True

    @action(
        detail=True,  # ⇒ URL c ID категории
        methods=["get"],
        url_path="brands",
        serializer_class=BrandSerializer,
    )
    def brands(self, request, *args, **kwargs):
        """
        GET /api/v1/categories/<slug>/brands/?city=Алматы
        Вернуть бренды категории, у которых в указанном городе есть
        хотя бы один товар с остатком > 0.
        """
        category = self.get_object()  # берём категорию из URL
        city_name = request.query_params.get("city")  # ?city=Алматы

        # --- базовый фильтр: связь brand ↔ product ↔ category
        brands_qs = Brands.objects.filter(
            products__category=category  # FK Product.category
        )

        # --- дополнительный фильтр по остаткам в городе (если город задан) + наличие фото
        photo_condition = Q(products__productimage__isnull=False)
        if city_name:
            brands_qs = brands_qs.filter(
                photo_condition,  # фото
                Q(products__stocks__warehouse__city__name_city=city_name)  # город
                & Q(products__stocks__quantity__gt=0),  # > 0 шт.
            )
        else:
            # если город не задан, просто убираем бренды без фото вообще
            brands_qs = brands_qs.filter(photo_condition)

        # --- финальные оптимизации ------------------------------------------------
        brands_qs = (
            brands_qs.distinct().prefetch_related(  # иначе дубликаты из-за JOIN-ов
                "logobrand_set"
            )  # или ваш реальный related-name
        )

        # --- стандартная пагинация DRF -------------------------------------------
        page = self.paginate_queryset(brands_qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(brands_qs, many=True)
        return Response(serializer.data)
