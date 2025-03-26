from django.http import JsonResponse
from django.db.models import Min, Max, Count, Sum
from django.contrib.contenttypes.models import ContentType

from rest_framework import viewsets
from rest_framework.response import Response

from app_sales_points.models import Stock, City
from app_category.models import Category
from app_products.models import Products
from app_sales_points.serializers import (
    StockSerializer,
    PriceRangeByCitySerializer,
    CitySerializer,
)

from app_products.ProductsQueryFactory import ProductsQueryFactory
from app_products.views_v2 import ProductsViewSet_v2


# class CityViewSet(viewsets.ReadOnlyModelViewSet):
#     БЕЗ УЧЕТА ЛОГИЧТИЧЕСКИХ РЕБЕР!!!!!!!!!!!!!!!
#     queryset = City.objects.all()
#     serializer_class = CitySerializer

#     def get_queryset(self):
#         return City.objects.annotate(
#             total_products=Count("warehouses__stocks__product", distinct=True),
#             # total_quality=Sum("warehouses__stocks__quantity"),
#         )


class StocksViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stock.objects.select_related(
        "warehouse__city", "product__category"
    ).all()
    serializer_class = StockSerializer

    def filter_by_prod(self, request, prod_pk, city_pk=None, *args, **kwargs):
        stocks = Stock.objects.filter(product_id=prod_pk, warehouse__city=city_pk)
        serializer = self.get_serializer(stocks, many=True)
        return Response(serializer.data)

    def get_prices_by_category(self, request, cat_pk):
        # Получаем категорию и все её подкатегории
        descendant_categories = (
            Category.objects.get(pk=cat_pk)
            .get_descendants(include_self=True)
            .values_list("id", flat=True)
        )

        # Получаем продукты из этих категорий
        product_ids = Products.objects.filter(
            category_id__in=descendant_categories
        ).values_list("id", flat=True)

        # Получаем цены на эти продукты, группируя по городам складов
        prices = (
            Stock.objects.filter(product_id__in=product_ids)
            .select_related("warehouse__city")
            .values("warehouse__city__name_city")
            .annotate(MinPrice=Min("price"), MaxPrice=Max("price"))
            .order_by("warehouse__city__name_city")
        )

        # Сериализуем данные
        serializer = PriceRangeByCitySerializer(prices, many=True)
        return Response(serializer.data)


def get_objects(request):
    content_type_id = request.GET.get("content_type")
    if not content_type_id:
        return JsonResponse({"objects": []})

    try:
        model_class = ContentType.objects.get(id=content_type_id).model_class()
        objects = model_class.objects.all()
        return JsonResponse(
            {"objects": [{"id": obj.id, "name": obj.get_name()} for obj in objects]}
        )
    except ContentType.DoesNotExist:
        return JsonResponse({"objects": []})


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CitySerializer

    def get_queryset(self):
        # Базово вернём все города (потом в list() аннотируем их полями)
        return City.objects.all()

    def list(self, request, *args, **kwargs):
        """
        Возвращает список городов, где у каждого города указано:
        - total_products: количество уникальных товаров, которые видны в этом городе (с учётом рёбер)
        - total_quantity: суммарный остаток по всем видимым товарам (т.е. те склады, которые физически в городе ИЛИ в городах, из которых есть ребро?)
          *в примере ниже — мы считаем сумму остатков только там, где физически хранится товар.
           Но если нужно учитывать "виртуальные" остатки, это спорный момент: возможно, нужно считать только склады, физически находящиеся в "своём" городе,
           или же суммировать склады "чужих" городов, если есть ребро?
        """
        cities = self.get_queryset()

        # Собираем аннотированный результат в формате city_id -> {...}
        city_stats = {}
        # Чтобы оптимизировать работу с товарами, возьмём базовый общий QuerySet:
        base_products_qs = ProductsQueryFactory.get_all_details()

        for city in cities:
            city_name = str(city.name_city)
            # 1) Все товары, доступные в этом городе
            visible_qs = ProductsViewSet_v2().filter_by_city_and_edges(
                base_products_qs, city_name
            )
            # 2) Аннотируем (на уровне Product) сумму остатков. Важно: физический склад лежит
            #    в "warehouse__city"? Но какие города считаем?
            #    - Обычно, если товар виден "по ребру", значит склад в другом городе, но всё равно товар "доступен".
            #    - Тогда sum_quantity — это сумма всех складов у этого товара.
            #      (Если хотите считать только "физические" остатки, нужно аккуратнее.)
            visible_qs = visible_qs.annotate(product_quantity=Sum("stocks__quantity"))

            total_products = visible_qs.count()  # кол-во уникальных товаров
            # Суммарная quantity всех видимых товаров (физ. остатки складов, где бы они ни были)
            total_quantity = 0
            for prod in visible_qs:
                total_quantity += prod.product_quantity or 0

            city_stats[city.id] = {
                "total_products": total_products,
                "total_quantity": total_quantity,
            }

        # Теперь сериализуем города
        serializer = self.get_serializer(cities, many=True)
        data = serializer.data

        # Подмешиваем цифры из city_stats
        for item in data:
            c_id = item["id"]
            stats = city_stats.get(c_id, {"total_products": 0, "total_quantity": 0})
            item["total_products"] = stats["total_products"]
            item["total_quantity"] = stats["total_quantity"]

        return Response(data)
