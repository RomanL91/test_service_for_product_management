from django.db import models

from app_products.models import Products


class Token(models.Model):
    token_value = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Токен",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name="Активен",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления",
    )

    class Meta:
        verbose_name = "Kaspi Токен"
        verbose_name_plural = "Kaspi Токены"

    def __str__(self):
        return self.token_value


class Customer(models.Model):
    customer_id = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="ID клиента в каспи",
    )
    cell_phone = models.CharField(
        max_length=15,
        verbose_name="Телефонный номер",
    )
    first_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Имя",
    )
    last_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Фамилия",
    )

    class Meta:
        verbose_name = "Kaspi Клиент"
        verbose_name_plural = "Kaspi Клиенты"

    def __str__(self):
        return f"{self.first_name} {self.cell_phone}"


class Product(models.Model):
    product_id = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="ID продукта в каспи",
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Название продукта",
    )
    prod_in_shop = models.OneToOneField(
        Products,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        to_field="vendor_code",
        verbose_name="Ссылка на продукт в Магазине",
    )
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Базовая цена",
    )
    vendor_code = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Код артикул",
    )

    class Meta:
        verbose_name = "Kaspi Продукт"
        verbose_name_plural = "Kaspi Продукты"

    def __str__(self):
        return self.name


class Order(models.Model):
    order_id = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="ID ордера",
    )
    code = models.CharField(
        max_length=100,
        verbose_name="Код ордера",
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Сумма ордера",
    )
    payment_mode = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Способ оплаты",
    )
    creation_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Время создания",
    )
    delivery_cost_for_seller = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Стоимость доставки",
    )
    is_kaspi_delivery = models.BooleanField(
        default=False,
        verbose_name="Каспи доставка?",
    )
    delivery_mode = models.CharField(
        max_length=100,
        verbose_name="Способ доставки",
    )
    pre_order = models.BooleanField(
        default=False,
        verbose_name="Предзаказ?",
    )
    state = models.CharField(
        max_length=100,
        verbose_name="Состояние ордера",
    )
    approved_by_bank_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Дата/время принятие банком",
    )
    status = models.CharField(
        max_length=100,
        verbose_name="Статус ордера",
    )
    product_in_orders = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        to_field="product_id",
        verbose_name="Ссылка на продукт Каспи",
    )
    customer_kaspi = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        to_field="customer_id",
        verbose_name="Ссылка на пользователя Каспи",
    )
    delivery_address = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        verbose_name="Адрес доставки",
    )
    latitude = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        verbose_name="Гео, ширина",
    )
    longitude = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        verbose_name="Гео, долгота",
    )

    def __str__(self):
        return self.order_id

    class Meta:
        verbose_name = "Каспи Заявка"
        verbose_name_plural = "Каспи Заявки"
