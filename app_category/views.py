from collections import defaultdict

from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view

from app_category.models import Category
from app_category.serializers import CategorySerializer

from app_products.models import Products
from app_products.serializers_v2 import ProductSerializer
from app_products.ProductsQueryFactory import ProductsQueryFactory
from app_products.views_v2 import ProductsViewSet_v2


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


# ------------ helpers -------------------------------------------------
def _parse_int_list(raw: str | None) -> list[int]:
    if not raw:
        return []
    return [int(v) for v in raw.split(",") if v.isdigit()]


def _apply_filters(qs, brand_ids: list[int], spec_filters: dict[int, list[int]]):
    """накладываем выбранные фильтры на qs"""
    if brand_ids:
        qs = qs.filter(brand_id__in=brand_ids)

    for spec_id, value_ids in spec_filters.items():
        qs = qs.filter(
            specifications__name_specification_id=spec_id,
            specifications__value_specification_id__in=value_ids,
        )

    return qs.distinct()


# ------------ сам эндпоинт -------------------------------------------
@api_view(["GET"])
def category_facets(request):
    """
    GET /categories/facets/
        - получим Бренды + Характеристики + Товары всей категории
    GET /categories/facets/?city=Караганда
        - получим Бренды + Характеристики + Товары всей категории от города и логистических ребер!
        - выходит нам всегда нужно помнить о фильтрации по городу!

    Пример более полной фильтрации
    GET /categories/facets/
       ?category=1,2--------фильтруем по категории
       &brand=1,2-----------фильтруем по брендам
       &city=Актобе---------фильтруем по городу
       &spec_12=5,6---------фильтруем по названию характеристики с ID 12 и значениями с ID 5 и 6 (&spec_<ЦВЕТ>=<БЕЛЫЙ>,<ЧЕРНЫЙ>)
       &limit=20&offset=0---пагинация
       +++ сортировка +++
       по цене, по сред рейтингу, по кол отзывов, по бренду (алфавит).
       &ordering=price(-price) - дешевый сначала
       &ordering=-reviews,-price - популярные (количество отзывов), дорогие внизу
       &ordering=brand,-rating - бренды по алфавиту, потом по рейтингу

       самое важно для понимания это:
       &spec_12=5,6
       где
       spec_12 - это ключ. spec_<ID ключа> - ключ формируется из приставки 'spec_' + ID название характеристики.
       =5,6 - это ID значения характеристики.
    """
    category_ids = _parse_int_list(request.GET.get("category"))
    category = Category.objects.filter(pk__in=category_ids)
    category_ids = category.get_descendants(include_self=True).values_list(
        "id", flat=True
    )
    if not category_ids:
        category_ids = Category.objects.all().values_list("id", flat=True)

    # ---------- выбранные фильтры ------------------
    brand_ids = _parse_int_list(request.GET.get("brand"))

    spec_filters: dict[int, list[int]] = {}
    for key, val in request.GET.items():
        if key.startswith("spec_"):
            spec_id = int(key.split("_")[1])
            spec_filters[spec_id] = _parse_int_list(val)

    # ---------- базовый узкий qs -------------------
    base_qs = Products.objects.filter(category_id__in=category_ids)
    base_qs = _apply_filters(base_qs, brand_ids, spec_filters)

    # ---------- гидрация через фабрику qs -------------------
    prod_qs = ProductsQueryFactory.enrich(base_qs)

    # ---------- фильтрация по городу -------------------
    city_name = request.GET.get("city")
    if city_name:
        # Фильтрация товаров по остаткам в указанном городе
        stocks_filter = Q(stocks__warehouse__city__name_city=city_name)

        # Фильтрация товаров по рёбрам, ведущим в указанный город
        edges_filter = Q(
            Q(category__edges__city_to__name_city=city_name)
            | Q(brand__edges__city_to__name_city=city_name)
        )

        # Применяем фильтры и удаляем дубли
        prod_qs = prod_qs.filter(stocks_filter | edges_filter)
    # ---------- сортировка -----------------------------
    ordering = request.GET.get("ordering")  # пример: ?ordering=price,-rating
    if ordering:
        # Разрешаем только перечисленные поля,
        # поддерживаем знак «-» для обратного порядка
        allowed = {
            "price": "stocks__price",
            "-price": "-stocks__price",
            "rating": "avg_rating",
            "-rating": "-avg_rating",
            "reviews": "reviews_count",
            "-reviews": "-reviews_count",
            "brand": "brand__name_brand",
            "-brand": "-brand__name_brand",
        }
        order_fields = [allowed[o] for o in ordering.split(",") if o in allowed]
        if order_fields:
            prod_qs = prod_qs.order_by(*order_fields)
    # ---------- counts для facets ------------------
    category_block = [
        {
            "id": cat_row["category_id"],
            "name": cat_row["category__name_category"],
            "count": cat_row["cnt"],
        }
        for cat_row in prod_qs.values("category_id", "category__name_category")
        .annotate(cnt=Count("id", distinct=True))
        .order_by("-cnt")
    ]
    brands_block = [
        {"id": row["brand_id"], "name": row["brand__name_brand"], "count": row["cnt"]}
        for row in prod_qs.values("brand_id", "brand__name_brand")
        .annotate(cnt=Count("id", distinct=True))
        .order_by("-cnt")
        if row["brand_id"]
    ]

    spec_rows = (
        prod_qs.values(
            "specifications__name_specification_id",
            "specifications__name_specification__name_specification",
            "specifications__value_specification_id",
            "specifications__value_specification__value_specification",
        )
        .annotate(cnt=Count("id", distinct=False))
        .order_by("-cnt")
    )
    print(f"--- spec_rows --- >>> {spec_rows}")

    spec_map: dict[int, dict] = defaultdict(
        lambda: {"id": None, "name": "", "values": []}
    )
    for r in spec_rows:
        sid = r["specifications__name_specification_id"]
        # if sid:
        spec_map[sid]["id"] = sid
        spec_map[sid]["name"] = r[
            "specifications__name_specification__name_specification"
        ]
        spec_map[sid]["values"].append(
            {
                "id": r["specifications__value_specification_id"],
                "value": r["specifications__value_specification__value_specification"],
                "count": r["cnt"],
            }
        )
    specs_block = list(spec_map.values())

    # ---------- блок товаров -----------------------
    limit = int(request.GET.get("limit", 20))
    offset = int(request.GET.get("offset", 0))

    # ---------- блок фильтрации по городу -----------------------
    # TODO я немного запутался, но считаю, что перенос этого блока выше правильное решение
    # # Фильтрация по городу, если указан
    # city_name = request.GET.get("city")
    # prod_qs = ProductsQueryFactory.enrich(base_qs)
    # if city_name:
    #     # Фильтрация товаров по остаткам в указанном городе
    #     stocks_filter = Q(stocks__warehouse__city__name_city=city_name)
    #     # Фильтрация товаров по рёбрам, ведущим в указанный город
    #     edges_filter = Q(
    #         Q(category__edges__city_to__name_city=city_name)
    #         | Q(brand__edges__city_to__name_city=city_name)
    #     )
    #     # Применяем фильтры и удаляем дубли
    #     prod_qs = prod_qs.filter(stocks_filter | edges_filter)

    page_qs = prod_qs[offset : offset + limit]

    serializer = ProductSerializer(page_qs, many=True)

    products_total = prod_qs.count()

    products_block = {
        "count": products_total,
        "limit": limit,
        "offset": offset,
        "items": serializer.data,
    }

    # ---------- ответ ------------------------------
    return Response(
        {
            "total": products_total,
            "categorys": category_block,
            "brands": brands_block,
            "specifications": specs_block,
            "products": products_block,
        },
        status=status.HTTP_200_OK,
    )
