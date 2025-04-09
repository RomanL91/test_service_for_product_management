# app_extproduct/signals.py
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import (
    ExtProduct,
    ExtProductImage,
    Stock as OldStock,
    Specifications as OldSpecs,
)
from app_products.models import Products, ProductImage
from app_sales_points.models import (
    Stock as NewStock,
    Warehouse as NewWarehouse,
    City as NewCity,
)
from app_specifications.models import (
    Specifications as NewSpecifications,
    NameSpecifications as NewNameSpecifications,
    ValueSpecifications as NewValueSpecifications,
)


@receiver(post_save, sender=ExtProduct)
def migrate_extproduct_to_new_models(sender, instance: ExtProduct, created, **kwargs):
    """
    После каждого сохранения ExtProduct пытаемся перенести данные
    в новые таблицы, если их там ещё нет.
    """
    # Если продукт уже перенесён — ничего не делаем
    if Products.objects.filter(vendor_code=instance.vendor_code).exists():
        return

    # Переносим после фиксации транзакции создания/изменения ExtProduct
    transaction.on_commit(lambda: _do_transfer(instance))


def _do_transfer(extp: ExtProduct):
    """
    Реальная логика переноса (почти 1‑в‑1 из вашего transfer_extproduct,
    но без request и лишних print).
    Выполняется уже **после** commit.
    """
    # 1. Создаём или находим Products
    new_product, created = Products.objects.get_or_create(
        vendor_code=extp.vendor_code,
        defaults={
            "name_product": extp.product_name,
            "category": extp.category,
            "brand": extp.brand,
        },
    )
    if not created:
        new_product.name_product = extp.product_name or new_product.name_product
        new_product.category = extp.category or new_product.category
        new_product.brand = extp.brand or new_product.brand
        new_product.save(update_fields=["name_product", "category", "brand"])

    # 2. Изображения
    for old_img in ExtProductImage.objects.filter(product=extp):
        ProductImage.objects.create(product=new_product, image=old_img.image)

    # 3. Склады / остатки
    for old_stock in OldStock.objects.filter(product=extp):
        new_wh = None
        if old_stock.warehouse:
            old_wh, old_city = old_stock.warehouse, old_stock.warehouse.city

            new_city = None
            if old_city:
                new_city, _ = NewCity.objects.get_or_create(
                    name_city=old_city.name_city
                )

            new_wh, _ = NewWarehouse.objects.get_or_create(
                external_id=old_wh.external_id,
                defaults={"name_warehouse": old_wh.name_warehouse, "city": new_city},
            )

        NewStock.objects.create(
            warehouse=new_wh,
            product=new_product,
            quantity=old_stock.quantity,
            price=old_stock.price,
        )

    # 4. Характеристики
    for old_spec in OldSpecs.objects.filter(product=extp):
        if not (old_spec.name_specification and old_spec.value_specification):
            continue
        new_name, _ = NewNameSpecifications.objects.get_or_create(
            name_specification=old_spec.name_specification.name_specification
        )
        new_value, _ = NewValueSpecifications.objects.get_or_create(
            value_specification=old_spec.value_specification.value_specification
        )
        NewSpecifications.objects.get_or_create(
            product=new_product,
            name_specification=new_name,
            value_specification=new_value,
        )

    # 5. Удаляем исходный товар — каскадно удалятся картинки и остатки
    extp.delete()
