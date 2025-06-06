from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.pagination import LimitOffsetPagination

from django.utils import timezone
from django.db.models import Q, Case, When, Value, IntegerField
from django.shortcuts import get_object_or_404

from app_category.models import Category
from app_products.models import PopulatesProducts

from app_products.serializers_v2 import ProductSerializer

from app_products.ProductsFiltering import ProductsFilter
from app_products.ProductsQueryFactory import ProductsQueryFactory

from django_filters.rest_framework import DjangoFilterBackend


class ProductsPagination(LimitOffsetPagination):
    default_limit = 20  # Переопределение значения limit
    # max_limit = 100  # Максимальный размер страницы


class ProductsViewSet_v2(ReadOnlyModelViewSet):
    """
    Представление только для чтения продуктов с аннотированной информацией.
    """

    queryset = ProductsQueryFactory.get_all_details()
    serializer_class = ProductSerializer
    pagination_class = ProductsPagination
    lookup_field = "slug"  # Указываем поле для поиска
    filter_backends = [
        OrderingFilter,
        SearchFilter,
        DjangoFilterBackend,
    ]
    filterset_class = ProductsFilter
    ordering_fields = [
        "avg_rating",
        "stocks__price",
    ]  # Поля для сортировки
    search_fields = [
        "name_product",
        "vendor_code",
        "category__name_category",
        "brand__name_brand",
        "additional_data",  # JSON
        "category__additional_data",  # JSON
        "brand__additional_data",  # JSON
    ]

    def filter_by_city_and_edges(self, queryset, city_name):
        """
        Фильтрует товары по остаткам и рёбрам для указанного города.
        """
        if not city_name:
            return queryset

        # Фильтрация товаров по остаткам в указанном городе
        stocks_filter = Q(stocks__warehouse__city__name_city=city_name)

        # Фильтрация товаров по рёбрам, ведущим в указанный город
        edges_filter = Q(
            Q(category__edges__city_to__name_city=city_name)
            | Q(brand__edges__city_to__name_city=city_name)
        )

        # Применяем фильтры и удаляем дубли
        return queryset.filter(stocks_filter | edges_filter).distinct()

    def list(self, request, *args, **kwargs):
        """
        Переопределяем метод list для применения фильтрации по городам.
        """
        # Получаем базовый QuerySet
        queryset = self.filter_queryset(self.get_queryset())

        # Проверяем наличие параметра `city`
        city_name = request.query_params.get("city")
        if city_name:
            queryset = self.filter_by_city_and_edges(queryset, city_name)

        # Применяем пагинацию
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Сериализация без пагинации
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="filter_by_ids")
    def filter_by_ids(self, request, *args, **kwargs):
        ids_param = request.query_params.get("ids")
        if not ids_param:
            return Response({"detail": "No 'ids' param"}, status=400)
        try:
            ids_list = [int(pk) for pk in ids_param.split(",") if pk.strip()]
        except ValueError:
            return Response({"detail": "Invalid 'ids' format"}, status=400)

        queryset = self.filter_queryset(self.get_queryset().filter(pk__in=ids_list))

        # Фильтрация по городу, если указан
        city_name = request.query_params.get("city")
        queryset = self.filter_by_city_and_edges(queryset, city_name)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="popular_set")
    def popular_set(self, request, *args, **kwargs):
        """
        Возвращает первый активный набор из PopulatesProducts.
        """
        populate_set = PopulatesProducts.objects.filter(activ_set=True).first()
        if not populate_set:
            raise NotFound({"detail": "No active populate set found."})

        # Получаем товары из активного набора
        product_ids = populate_set.products.values_list("id", flat=True)

        # Используем фабрику для аннотирования товаров
        queryset = (
            ProductsQueryFactory.get_all_details()
            .filter(id__in=product_ids)
            .order_by("productsetproduct__sort_value")
        )

        # Фильтрация по городу
        city_name = request.query_params.get("city")
        queryset = self.filter_by_city_and_edges(queryset, city_name)

        # Применяем сортировку
        queryset = self.filter_queryset(queryset)

        # Пагинация, если нужна
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def products_by_category(self, request, category_slug=None, *args, **kwargs):
        """
        Возвращает товары определённой категории и её подкатегорий.
        """
        # --------------------------------------------------------------------- #
        # 1. Базовый набор товаров категории и её потомков
        category = get_object_or_404(Category, slug=category_slug)
        category_ids = category.get_descendants(include_self=True).values_list(
            "id", flat=True
        )
        queryset = ProductsQueryFactory.get_all_details().filter(
            category_id__in=category_ids
        )

        # --------------------------------------------------------------------- #
        # 2. Фильтр по городу (ваша логика)
        city_name = request.query_params.get("city")
        queryset = self.filter_by_city_and_edges(queryset, city_name)

        # --------------------------------------------------------------------- #
        # 3. «Продвигаем» запрошенный бренд
        brand_param = request.query_params.get("brand")
        if brand_param and brand_param.isdigit():
            queryset = queryset.annotate(
                priority=Case(
                    When(
                        # Q(brand__id=brand_param) | Q(brand__slug=brand_param),
                        Q(brand__id=int(brand_param)),
                        then=Value(0),
                    ),
                    default=Value(1),
                    output_field=IntegerField(),
                )
            ).order_by(
                "priority",
            )

        # # --------------------------------------------------------------------- #
        # 4. Прочие сортировки через DRF OrderingFilter
        # queryset = self.filter_queryset(queryset)  # может вернуть .order_by(…)
        # print(f"---queryset --- > {queryset}")
        # print(f"--- self.ordering_fields --- > {self.ordering_fields}")

        # --------------------------------------------------------------------- #
        # это не работает! 4 и 5 шаги конфликтны!
        # 5. Если у нас есть поле priority — ставим его первым в order_by
        # if brand_param:
        # current_ordering = queryset.query.order_by
        # queryset = queryset.order_by("priority", *self.ordering_fields)

        # --------------------------------------------------------------------- #
        # 6. Пагинация / сериализация
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="filter_by_city")
    def filter_by_city(self, request, *args, **kwargs):
        """
        Фильтрует товары по городу с учётом остатков и рёбер.
        """
        city_name = request.query_params.get("city")
        if not city_name:
            return Response({"detail": "City parameter is required."}, status=400)

        queryset = self.filter_by_city_and_edges(self.get_queryset(), city_name)

        # Пагинация, если нужна
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="discounted")
    def discounted(self, request, *args, **kwargs):
        """
        Возвращает все товары, у которых сейчас действует скидка
        (product / category / brand) и которые «видны» в заданном городе.
        Обязательный query-param: ?city=<имя_города>
        """
        city_name = request.query_params.get("city")
        if not city_name:
            return Response(
                {"detail": "City parameter is required."},
                status=400,
            )

        # 1. Базовый набор с аннотациями/префетчами из фабрики
        qs = self.get_queryset()

        # 2. Ограничиваем городом (склады + рёбра)
        qs = self.filter_by_city_and_edges(qs, city_name)

        # 3. Фильтр «есть активная скидка прямо сейчас»
        now = timezone.now()

        discount_filter = (
            # Скидки на конкретные продукты
            Q(product_discounts__active=True)
            & (
                Q(product_discounts__start_date__isnull=True)
                | Q(product_discounts__start_date__lte=now)
            )
            & (
                Q(product_discounts__end_date__isnull=True)
                | Q(product_discounts__end_date__gte=now)
            )
            # Скидки на категории
            | Q(category__category_discounts__active=True)
            & (
                Q(category__category_discounts__start_date__isnull=True)
                | Q(category__category_discounts__start_date__lte=now)
            )
            & (
                Q(category__category_discounts__end_date__isnull=True)
                | Q(category__category_discounts__end_date__gte=now)
            )
            # Скидки на бренды
            | Q(brand__brand_discounts__active=True)
            & (
                Q(brand__brand_discounts__start_date__isnull=True)
                | Q(brand__brand_discounts__start_date__lte=now)
            )
            & (
                Q(brand__brand_discounts__end_date__isnull=True)
                | Q(brand__brand_discounts__end_date__gte=now)
            )
        )

        qs = qs.filter(discount_filter).distinct()
        qs = self.filter_queryset(qs)

        brands_to_filter = qs.values(
            "brand__id", "brand__name_brand", "brand__logobrand__image"
        )
        cat_to_filter = qs.values(
            "category__id",
            "category__name_category",
            "category__slug",
            "category__categoryimage__image",
        ).distinct()
        spec_to_filter = qs.values(
            "specifications__name_specification__name_specification",
            "specifications__value_specification__value_specification",
        ).distinct()
        response_data: dict = {
            "brands_to_filter": brands_to_filter,
            "cat_to_filter": cat_to_filter,
            "spec_to_filter": spec_to_filter,
        }

        # 4. Пагинация / сериализация
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response_data.setdefault("prod", serializer.data)
            return self.get_paginated_response(response_data)

        serializer = self.get_serializer(qs, many=True)
        response_data.setdefault("prod", serializer.data)

        return Response(response_data)
