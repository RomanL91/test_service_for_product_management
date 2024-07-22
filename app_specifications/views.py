from rest_framework import viewsets
from rest_framework.response import Response

from app_specifications.models import Specifications
from app_category.models import Category
from app_specifications.serializers import SpecificationsSerializer


class SpecificationsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Specifications.objects.select_related(
        "name_specification", "value_specification"
    )
    serializer_class = SpecificationsSerializer

    def filter_by_prod(self, request, prod_pk, *args, **kwargs):
        specif = Specifications.objects.filter(product_id=prod_pk)
        serializer = self.get_serializer(specif, many=True)
        return Response(serializer.data)

    def filter_by_cat(self, request, cat_pk):
        # Находим категорию и все её подкатегории
        descendant_categories = (
            Category.objects.get(pk=cat_pk)
            .get_descendants(include_self=True)
            .values_list("id", flat=True)
        )

        # Получаем характеристики для продуктов, которые принадлежат этим категориям
        specifications = Specifications.objects.filter(
            product__category__id__in=descendant_categories
        ).select_related("name_specification", "value_specification")

        # Сериализуем данные
        serializer = self.get_serializer(specifications, many=True)
        return Response(serializer.data)

    def get_specif_product_configurations(self, request, ids=None, *args, **kwargs):
        ids_products = [i for i in ids.split(",") if i.isdigit()]
        specifications = Specifications.objects.filter(
            product__id__in=ids_products
        ).select_related("name_specification", "value_specification")
        serializer = self.get_serializer(specifications, many=True)
        return Response(serializer.data)
