from django.db import models


class Category(models.Model):
    name_category = models.CharField(max_length=100)
    desc_category = models.TextField(
        verbose_name="Описание категории", max_length=1000, blank=True
    )
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, blank=True, null=True, related_name="children"
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name_category
