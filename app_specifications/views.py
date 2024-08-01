from rest_framework import viewsets
from rest_framework.response import Response

from django.shortcuts import get_object_or_404

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
    
    def filter_specif_by_category(self, **category_filter):
        # Получаем категорию по заданному фильтру (id или slug)
        category = get_object_or_404(Category, **category_filter)
        # Находим все подкатегории
        descendant_categories = category.get_descendants(include_self=True).values_list(
            "id", flat=True
        )
        # Фильтруем характеристики по этим категориям
        brands = (
            Specifications.objects.filter(product__category__id__in=descendant_categories)
            .distinct()
            .order_by("name_specification")
        )
        # Сериализуем и возвращаем данные
        serializer = self.get_serializer(brands, many=True)
        return Response(serializer.data)

    def filter_by_cat_id(self, request, cat_pk):
        return self.filter_specif_by_category(id=cat_pk)
    
    def filter_by_cat_slug(self, request, cat_slug):
        return self.filter_specif_by_category(slug=cat_slug)
      

    def get_specif_product_configurations(self, request, ids=None, *args, **kwargs):
        ids_products = [i for i in ids.split(",") if i.isdigit()]
        specifications = Specifications.objects.filter(
            product__id__in=ids_products
        ).select_related("name_specification", "value_specification")
        serializer = self.get_serializer(specifications, many=True)
        return Response(serializer.data)
