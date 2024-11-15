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
