from rest_framework import viewsets
from rest_framework.response import Response

from django.shortcuts import get_object_or_404

from app_brands.models import Brands
from app_category.models import Category
from app_brands.serializers import BrandsSerializer


class BrandsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Brands.objects.all()
    serializer_class = BrandsSerializer

    def filter_brands_by_category(self, **category_filter):
        # Получаем категорию по заданному фильтру (id или slug)
        category = get_object_or_404(Category, **category_filter)
        # Находим все подкатегории
        descendant_categories = category.get_descendants(include_self=True).values_list(
            "id", flat=True
        )
        # Фильтруем бренды по этим категориям
        brands = (
            Brands.objects.filter(products__category__id__in=descendant_categories)
            .distinct()
            .order_by("name_brand")
        )
        # Сериализуем и возвращаем данные
        serializer = self.get_serializer(brands, many=True)
        return Response(serializer.data)

    def filter_by_cat_id(self, request, cat_pk):
        return self.filter_brands_by_category(id=cat_pk)

    def filter_by_cat_slug(self, request, cat_slug):
        return self.filter_brands_by_category(slug=cat_slug)
