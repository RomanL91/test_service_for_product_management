import uuid
from enum import Enum
from decimal import Decimal
from random import randint

from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(default=now, null=True)
    updated_at = models.DateTimeField(default=now, null=True)

    class Meta:
        abstract = True


def generate_account_number():
    return randint(100000000, 999999999)


# Django аналог Enum
class CheckoutStageSchema(Enum):
    CREATED = "created"
    PROCESSING = "processing"
    COMPLETED = "completed"

    @classmethod
    def choices(cls):
        return [(tag.name, tag.value) for tag in cls]


class Baskets(BaseModel):
    uuid_id = models.CharField(
        unique=True, default=uuid.uuid4
    )  # UUIDField с уникальным значением
    user_id = models.UUIDField(
        null=True, blank=True
    )  # UUID пользователя (сопоставление SQLAlchemy UUID)
    completed = models.BooleanField(
        default=False, null=True, blank=True
    )  # Поле для статуса
    checkout_stage = models.CharField(
        max_length=20,
        choices=CheckoutStageSchema.choices(),
        default=CheckoutStageSchema.CREATED.value,  # Аналог Enum по строковому значению
    )
    basket_items = models.JSONField(null=True, blank=True, default=list)  # JSON аналог
    gift_items = models.JSONField(null=True, blank=True, default=list)  # JSON аналог

    class Meta:
        db_table = "baskets"
        managed = False

    def __str__(self):
        return f"Basket id={self.id}, uuid_id={self.uuid_id}"

    def __repr__(self):
        return self.__str__()


# Перечисления
class PaymentType(models.TextChoices):
    ONLINE = "ONLINE", _("ONLINE")
    OFFLINE = "OFFLINE", _("OFFLINE")


class OrderStatusType(models.TextChoices):
    NEW = "NEW", _("NEW")
    INWORK = "INWORK", _("INWORK")
    COMPLETED = "COMPLETED", _("COMPLETED")
    CANCELED = "CANCELED", _("CANCELED")


class PaymentStatus(models.TextChoices):
    PAID = "PAID", _("PAID")
    UNPAID = "UNPAID", _("UNPAID")


class DeliveryType(models.TextChoices):
    PICKUP = "PICKUP", _("PICKUP")
    DELIVERY = "DELIVERY", _("DELIVERY")


class Orders(models.Model):
    # ФИО пользователя
    user_full_name = models.CharField(max_length=255)
    # ID пользователя
    user_id = models.UUIDField()
    # Общая сумма заказа
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.0")
    )
    # Номер счета для банка
    account_number = models.IntegerField(unique=True, default=generate_account_number)
    # Тип оплаты
    payment_type = models.CharField(
        max_length=20,
        choices=PaymentType.choices,
        default=PaymentType.ONLINE,
    )
    # Связь с корзиной
    uuid_id = models.ForeignKey(
        "Baskets",
        to_field="uuid_id",
        db_column="uuid_id",
        on_delete=models.CASCADE,
        unique=True,
    )
    # Статус заказа
    order_status = models.CharField(
        max_length=20,
        choices=OrderStatusType.choices,
        default=OrderStatusType.NEW,
    )
    # Статус платежа
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.UNPAID,
    )
    # Комментарий к заказу
    comment = models.TextField(null=True, blank=True)
    # Номер телефона
    phone_number = models.CharField(max_length=20)
    # Email
    email = models.EmailField(null=True, blank=True)
    # Город доставки
    shipping_city = models.CharField(max_length=255)
    # Адрес доставки
    delivery_address = models.TextField(null=True, blank=True)
    # Тип доставки
    delivery_type = models.CharField(
        max_length=20,
        choices=DeliveryType.choices,
        default=DeliveryType.DELIVERY,
    )
    # Менеджер, ответственный за выполнение заказа
    manager_executive = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "orders"
        managed = False

    def __str__(self):
        return f"Order #{self.account_number} ({self.user_full_name})"
