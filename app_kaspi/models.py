from django.db import models


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
        verbose_name = "Токен"
        verbose_name_plural = "Токены"

    def __str__(self):
        return self.token_value


class Customer(models.Model):
    customer_id = models.CharField(max_length=100, unique=True)
    cell_phone = models.CharField(max_length=15, unique=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Клиент Kaspi"
        verbose_name_plural = "Клиенты Kaspi"

    def __str__(self):
        return self.customer_id


class Address(models.Model):
    street_name = models.CharField(max_length=255)
    street_number = models.CharField(max_length=100)
    town = models.CharField(max_length=255)
    district = models.CharField(max_length=255, blank=True, null=True)
    building = models.CharField(max_length=255, blank=True, null=True)
    apartment = models.CharField(max_length=50, blank=True, null=True)
    formatted_address = models.CharField(max_length=500)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.formatted_address


class KaspiDelivery(models.Model):
    waybill = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Накладная"
    )
    courier_transmission_date = models.DateTimeField(
        blank=True, null=True, verbose_name="Дата передачи курьеру"
    )
    courier_transmission_planning_date = models.BigIntegerField(
        blank=True, null=True, verbose_name="Плановая дата передачи курьеру"
    )
    waybill_number = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Номер накладной"
    )
    express = models.BooleanField(default=False, verbose_name="Экспресс доставка")
    returned_to_warehouse = models.BooleanField(
        default=False, verbose_name="Возвращено на склад"
    )
    first_mile_courier = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Первомильный курьер"
    )

    class Meta:
        verbose_name = "Доставка Kaspi"
        verbose_name_plural = "Доставки Kaspi"

    def __str__(self):
        return f"Kaspi Delivery {self.id}"


from app_products.models import Products


class Product(models.Model):
    product_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    code = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    category = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    prod_in_shop = models.OneToOneField(
        Products, on_delete=models.SET_NULL, blank=True, null=True
    )
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Базовая цена",
    )
    vendor_code = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Код артикул"
    )

    class Meta:
        verbose_name = "Каспи Продукт"
        verbose_name_plural = "Каспи Продукты"

    def __str__(self):
        return self.name


class Order(models.Model):
    order_id = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=100)
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    payment_mode = models.CharField(max_length=100, blank=True, null=True)
    creation_date = models.DateTimeField(blank=True, null=True)
    delivery_cost_for_seller = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    is_kaspi_delivery = models.BooleanField(default=False)
    delivery_mode = models.CharField(max_length=100)
    signature_required = models.BooleanField(default=False)
    credit_term = models.IntegerField(null=True)
    pre_order = models.BooleanField(default=False)
    pickup_point_id = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    approved_by_bank_date = models.BigIntegerField()
    status = models.CharField(max_length=100)
    product_in_orders = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True
    )
    kaspi_delivery = models.ForeignKey(
        KaspiDelivery, on_delete=models.SET_NULL, null=True, blank=True
    )
    customer_kaspi = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True
    )
    delivery_address_default = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return self.order_id

    class Meta:
        verbose_name = "Каспи Заявка"
        verbose_name_plural = "Каспи Заявки"
