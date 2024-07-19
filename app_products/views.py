from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count, Min, OuterRef, Prefetch, Subquery

from rest_framework import viewsets
from rest_framework.response import Response

from app_products.models import Products, PopulatesProducts
from app_discounts.models import ProductDiscount, CategoryDiscount
from app_sales_points.models import Stock
from app_category.models import Category
from app_products.serializers import (
    ProductsListSerializer,
    ProductsDetailSerializer,
    PrductsListIDSerializer,
    PopulatesProductsSerializer,
)


class PopulatesProductsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PopulatesProducts.objects.filter(activ_set=True)
    serializer_class = PopulatesProductsSerializer


class ProductsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductsListSerializer
    lookup_field = "slug_prod"

    def retrieve(self, request, slug_prod=None, *args, **kwargs):
        instance = self.get_object_by_slug(slug_prod)
        self.serializer_class = ProductsDetailSerializer
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        annotated_queryset = self.get_annotated_queryset(queryset)
        page = self.paginate_queryset(annotated_queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(annotated_queryset, many=True)
        return Response(serializer.data)

    def filter_by_cat(self, request, slug_cat=None, *args, **kwargs):
        queryset = self.get_products_by_category(slug_cat)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_object_by_slug(self, slug):
        queryset = self.get_annotated_queryset(Products.objects.filter(slug=slug))
        return queryset.first()

    def create_discount_subquery(self, model, filter_key):
        current_time = timezone.now()
        return (
            model.objects.filter(
                **{filter_key: OuterRef("pk")},
                active=True,  # Ищу только активные
                start_date__lte=current_time,  # Скидка началась не позже текущего времени
                end_date__gte=current_time,  # Скидка не закончится до текущего времени
            )
            .order_by()
            .values("amount")[:1]  # Возвращаем только первую активную скидку
        )

    def get_annotated_queryset(self, queryset):
        city_prices_subquery = (
            Stock.objects.filter(
                product_id=OuterRef("pk"),
                quantity__gt=0,  # Добавляем условие, чтобы учитывать только склады с остатком больше нуля
            )
            .values("warehouse__city")
            .annotate(min_price=Min("price"))
            .values("min_price")  # Возвращаем только один столбец
        )

        discount_subquery_p = self.create_discount_subquery(
            ProductDiscount, "products__id"
        )
        discount_subquery_c = self.create_discount_subquery(
            CategoryDiscount, "categories__products__id"
        )

        return queryset.annotate(
            average_rating=Avg("review__rating"),
            reviews_count=Count("review"),
            city_prices=Subquery(city_prices_subquery),
            discount_amount_p=Subquery(discount_subquery_p),
            discount_amount_c=Subquery(discount_subquery_c),
        ).prefetch_related(
            Prefetch(
                "stocks",
                queryset=Stock.objects.select_related("warehouse__city"),
            )
        )

    def get_products_by_category(self, slug_cat):
        # Получаем все товары, связанные с этой категорией
        products_queryset = self.queryset.filter(category__slug=slug_cat)

        # Если в категории нет продуктов, рекурсивно получаем продукты из всех подкатегорий
        if not products_queryset.exists():
            category = get_object_or_404(Category, slug=slug_cat)

            # Получаем все подкатегории данной категории
            subcategories = category.children.all()

            # Рекурсивно обходим каждую подкатегорию
            for subcategory in subcategories:
                products_queryset |= self.get_products_by_category(subcategory.slug)
        products_queryset = self.get_annotated_queryset(products_queryset)
        return products_queryset

    def slugs(self, request):
        self.serializer_class = PrductsListIDSerializer
        products_queryset = self.get_queryset()
        serializer = self.get_serializer(products_queryset, many=True)
        slugs = [el["slug"] for el in serializer.data]
        return Response(slugs)

    def vendor_cods(self, request):
        self.serializer_class = PrductsListVendorCodeSerializer
        products_queryset = self.get_queryset().order_by("vendor_code")
        serializer = self.get_serializer(products_queryset, many=True)
        return Response(serializer.data)

    def get_products_by_ids(self, *args, **kwargs):
        # Фильтрация продуктов по списку идентификаторов
        ids = kwargs.get("ids", [])
        ids_list = [i for i in ids.split(",") if i.isdigit()]
        queryset = Products.objects.filter(id__in=ids_list)
        annotated_queryset = self.get_annotated_queryset(queryset)
        serializer = self.get_serializer(annotated_queryset, many=True)
        return Response(serializer.data)


# @method_decorator(csrf_exempt, name="dispatch")
class ProductFilterView(APIView):

    def post(self, request, *args, **kwargs):
        # {
        #     "category": 3,
        #     "brand": 1,
        #     "price_min": 333,
        #     "price_max": 5000,
        #     "specifications": [{"name": "диагональ", "value": "15"}],
        # }
        data = request.data
        category_id = data.get("category")
        brand_id = data.get("brand")
        price_min = data.get("price_min")
        price_max = data.get("price_max")
        specs = data.get("specifications", [])

        # Используем select_related для загрузки связанных данных через ForeignKey
        # Используем prefetch_related для загрузки связанных данных через ManyToManyField и reverse ForeignKey
        query = Products.objects.select_related("brand", "category").prefetch_related(
            Prefetch(
                "specifications",
                queryset=Specifications.objects.select_related(
                    "name_specification", "value_specification"
                ),
            ),
            Prefetch("stocks", queryset=Stock.objects.select_related("warehouse")),
        )

        if category_id:
            query = query.filter(category_id=category_id)
        if brand_id:
            query = query.filter(brand_id=brand_id)
        if price_min is not None and price_max is not None:
            query = query.filter(
                stocks__price__gte=price_min, stocks__price__lte=price_max
            )

        # Фильтрация по спецификациям
        for spec in specs:
            name_spec = spec.get("name")
            value_spec = spec.get("value")
            query = query.filter(
                specifications__name_specification__name_specification=name_spec,
                specifications__value_specification__value_specification=value_spec,
            )

        # Используем distinct() для избежания дублирования продуктов при множественных фильтрациях
        query = query.distinct()

        serializer = PrductsListIDSerializer(query, many=True)
        return Response(serializer.data)
