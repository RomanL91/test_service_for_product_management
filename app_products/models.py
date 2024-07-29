from slugify import slugify

from django.db import models, transaction

from core.mixins import JSONFieldsMixin, SlugModelMixin

from app_brands.models import Brands
from app_category.models import Category
from app_manager_tags.models import Tag


class Products(JSONFieldsMixin, SlugModelMixin, models.Model):
    vendor_code = models.CharField(
        unique=True,
        max_length=30,
        verbose_name="Артикул продукта",
    )
    name_product = models.CharField(
        max_length=150,
        verbose_name="Наименование продукта",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="products",
        verbose_name="Категория продукта",
    )
    brand = models.ForeignKey(
        Brands,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="бренд продукта",
    )
    configuration = models.ManyToManyField(
        "self",
        blank=True,
        verbose_name="Комплектации",
    )
    related_product = models.ManyToManyField(
        "self",
        blank=True,
        verbose_name="Сопутствующий товар",
    )
    tag_prod = models.ManyToManyField(
        Tag,
        blank=True,
        verbose_name="Теги продукта",
    )
    present = models.ManyToManyField(
        "self",
        blank=True,
        verbose_name="В подарок",
    )
    services = models.ManyToManyField(
        "app_services.service",
        # related_name='products',
        blank=True,
        verbose_name="Услуги к продукту",
    )

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name_product)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name_product


class ProductImage(models.Model):
    image = models.ImageField(
        verbose_name="Изображение",
        blank=True,
        upload_to="product_images/%Y/%m/%d/%H/%M/%S/",
    )
    product = models.ForeignKey(
        Products,
        on_delete=models.CASCADE,
        verbose_name="Продукт",
    )

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"

    def __str__(self) -> str:
        return self.product.name_product


class PopulatesProducts(models.Model):
    name_set = models.CharField(
        max_length=150,
        verbose_name="Название сета",
    )
    activ_set = models.BooleanField(
        verbose_name="Активность набора",
        default=False,
    )
    products = models.ManyToManyField(
        Products,
        blank=True,
        verbose_name="Список популярных продуктов",
    )

    class Meta:
        verbose_name = "Популярный продукт"
        verbose_name_plural = "Популярные продукты"

    def __str__(self) -> str:
        return self.name_set


class ExternalProduct(models.Model):
    product_name = models.CharField(
        max_length=255,
        verbose_name="Наименование товара",
        blank=True,
    )
    product_code = models.CharField(
        max_length=30,
        verbose_name="Код товара",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена",
        blank=True,
    )
    stock = models.IntegerField(
        verbose_name="Остаток",
        blank=True,
    )
    warehouse_code = models.CharField(
        max_length=10,
        verbose_name="Код склада",
        blank=True,
    )
    slug = models.SlugField(
        max_length=200,
        blank=True,
        null=True,
        default=None,
    )

    # Добавим обязательные поля из модели Products
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        verbose_name="Категория продукта",
        related_name="external_products",
    )
    brand = models.ForeignKey(
        Brands,
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        verbose_name="Бренд продукта",
        related_name="external_products",
    )

    class Meta:
        verbose_name = "Внешний Продукт"
        verbose_name_plural = "Внешние Продукты"

    def __str__(self):
        return f"{self.product_name} ({self.product_code})"


class ExternalProductImage(models.Model):
    image = models.ImageField(
        verbose_name="Изображение",
        blank=True,
        upload_to="product_images/%Y/%m/%d/%H/%M/%S/",
    )
    external_product = models.ForeignKey(
        ExternalProduct,
        on_delete=models.CASCADE,
        verbose_name="Продукт",
    )

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"

    def __str__(self) -> str:
        return self.external_product.product_name


# ===============================SIGNALS========================================
from django.db.models.signals import post_save
from django.dispatch import receiver
from app_sales_points.models import Stock, Warehouse


@receiver(post_save, sender=ExternalProduct)
def create_or_update_product(sender, instance, **kwargs):
    with transaction.atomic():
        product, created = Products.objects.get_or_create(
            vendor_code=instance.product_code,
            defaults={
                "name_product": instance.product_name,
                "category": instance.category,
                "brand": instance.brand,
                "slug": slugify(instance.product_name),
            },
        )

    def remove_external_product():
        # Получение списка изображений из базы данных
        current_images = ProductImage.objects.filter(product=product)
        external_images = ExternalProductImage.objects.filter(external_product=instance)
        # Создание множества путей текущих изображений
        current_image_paths = {img.image.path for img in current_images}
        # Проверка и добавление новых изображений
        for img in external_images:
            if img.image.path not in current_image_paths:
                ProductImage.objects.create(product=product, image=img.image)

        # Создание множества путей внешних изображений
        new_image_paths = {img.image.path for img in external_images}
        # Удаление устаревших изображений
        for img in current_images:
            if img.image.path not in new_image_paths:
                img.delete()

        warehouse = Warehouse.objects.filter(
            external_id=instance.warehouse_code
        ).first()

        # Обновление или создание записей о запасах
        stock, created = Stock.objects.update_or_create(
            warehouse=warehouse,
            product=product,
            defaults={
                "quantity": instance.stock,
                "price": instance.price,
            },
        )

        instance.delete()

    transaction.on_commit(remove_external_product)
