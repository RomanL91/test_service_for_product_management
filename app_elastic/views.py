import abc

from elasticsearch_dsl import Q
from django.http import HttpResponse, JsonResponse
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.views import APIView

from app_category.documents import CategoryDocument
from app_products.documents import ProductDocument

from app_category.serializers import CategorySerializerElastic
from app_products.serializers import ProductsDetailSerializerSearch


class PaginatedElasticSearchAPIView(APIView, LimitOffsetPagination):
    serializer_class = None
    document_class = None

    @abc.abstractmethod
    def generate_q_expression(self, query):
        """This method should be overridden
        and return a Q() expression."""

    def get(self, request, query):
        try:
            # Создаем Q-запрос
            q = self.generate_q_expression(query)
            search = self.document_class.search().query(q)
            response = search.execute()

            # Преобразуем результаты поиска в список
            results = [hit.to_dict() for hit in response]

            serializer = self.serializer_class(results, many=True)
            return JsonResponse(serializer.data, safe=False)

        except Exception as e:
            return HttpResponse(str(e), status=500)


class SearchCategories(PaginatedElasticSearchAPIView):
    serializer_class = CategorySerializerElastic
    document_class = CategoryDocument

    def generate_q_expression(self, query):

        return Q(
            "bool",
            should=[
                Q("match", name_category=query),
                Q("match", slug=query),
                Q("match", additional_data=query),
            ],
            minimum_should_match=1,
        )


class SearchProducts(PaginatedElasticSearchAPIView):
    serializer_class = ProductsDetailSerializerSearch
    document_class = ProductDocument

    def generate_q_expression(self, query):
        # Используем `bool` запрос для поиска по нескольким полям
        return Q(
            "bool",
            should=[
                Q("match", vendor_code=query),
                Q("match", name_product=query),
                Q("match", slug=query),
                Q("match", category__name_category=query),
                Q("match", brand__name_brand=query),
                Q("match", additional_data=query),
                Q(
                    "nested",
                    path="tag_prod",
                    query=Q("match", tag_prod__tag_text=query),
                ),
                Q(
                    "nested",
                    path="specifications",
                    query=Q(
                        "bool",
                        should=[  # Используем should, чтобы искать либо по имени, либо по значению характеристики
                            Q("match", specifications__name_specification=query),
                            Q("match", specifications__value_specification=query),
                        ],
                        minimum_should_match=1,  # Требуем совпадения хотя бы по одному
                    ),
                ),
            ],
            minimum_should_match=1,
        )


class FilterProducts(PaginatedElasticSearchAPIView):
    serializer_class = ProductsDetailSerializerSearch
    document_class = ProductDocument

    def parse_specifications(self, filters):
        """Обработка повторяющихся параметров spec_name и spec_value"""
        spec_names = filters.getlist("spec_name")
        spec_values = filters.getlist("spec_value")

        # Создаем список характеристик из повторяющихся параметров
        specifications = []
        for name, value in zip(spec_names, spec_values):
            specifications.append({"spec_name": name, "spec_value": value})

        return specifications

    def generate_filter_query(self, filters):
        """Создает фильтры для Elasticsearch запроса"""
        filter_queries = []

        # Фильтр по категории
        if filters.get("category"):
            filter_queries.append(
                Q("match", category__name_category=filters["category"])
            )

        # Фильтр по брендам
        if filters.getlist("brand"):
            brands = filters.getlist("brand")  # Получаем список брендов
            filter_queries.append(Q("terms", brand__name_brand=brands))

        # Фильтр по тегам
        if filters.get("tag"):
            filter_queries.append(
                Q(
                    "nested",
                    path="tag_prod",
                    query=Q("match", tag_prod__tag_text=filters["tag"]),
                )
            )

        # Фильтр по характеристикам
        if filters.get("specifications"):
            specs = filters["specifications"]
            spec_queries = []
            for spec in specs:
                spec_queries.append(
                    Q(
                        "nested",
                        path="specifications",
                        query=Q(
                            "bool",
                            must=[
                                Q(
                                    "term",
                                    specifications__name_specification=spec[
                                        "spec_name"
                                    ],
                                ),
                                Q(
                                    "term",
                                    specifications__value_specification=spec[
                                        "spec_value"
                                    ],
                                ),
                            ],
                        ),
                    )
                )
            # Добавляем все спецификации в запрос как should (логическое OR)
            if spec_queries:
                filter_queries.append(
                    Q("bool", should=spec_queries, minimum_should_match=1)
                )

        # Фильтр по диапазону значений
        if filters.get("price_min") or filters.get("price_max"):
            price_filter = {}
            if filters.get("price_min"):
                price_filter["gte"] = filters["price_min"]
            if filters.get("price_max"):
                price_filter["lte"] = filters["price_max"]
            filter_queries.append(Q("range", price=price_filter))

        return filter_queries

    def get(self, request, *args, **kwargs):
        try:
            # Получаем фильтры из GET параметров
            filters = request.GET.copy()  # Копируем параметры запроса
            specifications = self.parse_specifications(filters)  # Парсим характеристики

            # Добавляем характеристики в фильтры
            if specifications:
                filters["specifications"] = specifications

            filter_queries = self.generate_filter_query(filters)

            # Создаем базовый запрос
            search_query = Q("bool", filter=filter_queries)

            # Выполняем запрос к Elasticsearch
            search = self.document_class.search().query(search_query)
            response = search.execute()

            # Преобразуем результаты поиска
            results = [hit.to_dict() for hit in response]
            serializer = self.serializer_class(results, many=True)
            return JsonResponse(serializer.data, safe=False)

        except Exception as e:
            return HttpResponse(str(e), status=500)
