from rest_framework import viewsets
from rest_framework.response import Response

from app_brands.models import Brands
from app_category.models import Category
from app_brands.serializers import BrandsSerializer


class BrandsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Brands.objects.all()
    serializer_class = BrandsSerializer

    def filter_by_cat(self, request, cat_pk):
        # Находим категорию и все её подкатегории
        descendant_categories = (
            Category.objects.get(pk=cat_pk)
            .get_descendants(include_self=True)
            .values_list("id", flat=True)
        )
        # Получаем продукты, которые принадлежат этим категориям
        brands = (
            Brands.objects.filter(products__category__id__in=descendant_categories)
            .distinct()
            .order_by("name_brand")
        )

        serializer = self.get_serializer(brands, many=True)
        return Response(serializer.data)
