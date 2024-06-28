from django.db import models

from core.mixins import JSONFieldsMixin, JSONFieldsDescMixin

from app_products.models import Products


class Blog(JSONFieldsMixin, JSONFieldsDescMixin, models.Model):
    title_blog = models.CharField(
        max_length=150,
        verbose_name="Заголовок блога",
    )
    body_blog = models.TextField(
        verbose_name="Текст блога",
    )
    related_product = models.ManyToManyField(
        Products,
        blank=True,
        verbose_name="Сопутствующий товар",
    )

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"

    def __str__(self) -> str:
        return self.title_blog


class BlogImage(models.Model):
    image = models.ImageField(
        verbose_name="Изображение",
        blank=True,
        upload_to="product_images/%Y/%m/%d/%H/%M/%S/",
    )
    blog = models.ForeignKey(
        Blog,
        on_delete=models.CASCADE,
        verbose_name="Продукт",
    )

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"

    def __str__(self) -> str:
        return self.blog.title_blog
