import uuid
from enum import Enum
from decimal import Decimal
from random import randint

from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    id = models.AutoField(
        primary_key=True,
        verbose_name="ИД записи в системе",
        help_text="""
            ИД записи в Базе Данных
        """,
    )
    created_at = models.DateTimeField(
        default=now,
        null=True,
        verbose_name="Время создания",
        help_text="""
            Время создания записи
        """,
    )
    updated_at = models.DateTimeField(
        default=now,
        null=True,
        verbose_name="Время обновления",
        help_text="""
            Время последнего изменения записи
        """,
    )

    class Meta:
        abstract = True


def generate_account_number():
    return randint(100000000, 999999999)


# Django аналог Enum
class CheckoutStageSchema(Enum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    # COMPLETED = "completed"

    @classmethod
    def choices(cls):
        return [(tag.name, tag.value) for tag in cls]


class Baskets(BaseModel):
    uuid_id = models.CharField(
        unique=True,
        default=uuid.uuid4,
        verbose_name="Уникальный ИД устройства",
        help_text="""
            Этот ИД, создается на устройве пользователя и хранится на нем до тех пор, 
            пока корзина пользователя не будет оформлена в заявку       
        """,
    )  # UUIDField с уникальным значением
    user_id = models.UUIDField(
        null=True,
        blank=True,
        verbose_name="ИД зарегистрированного пользователя",
        help_text="""
            Это ИД самого пользователя в системе, то есть при наличии этого значения у корзины,
            можно считать ее подписанной пользователем, который авторизовался в системе
        """,
    )  # UUID пользователя (сопоставление SQLAlchemy UUID)
    completed = models.BooleanField(
        default=False,
        null=True,
        blank=True,
        verbose_name="Логический статус корзины",
        help_text="""
            Данный логический статус равен ИСТИНЕ, если корзина оформлена и заявка на нее оплачена,
            иначе значение равно ЛОЖЬ
        """,
    )  # Поле для статуса
    checkout_stage = models.CharField(
        max_length=20,
        choices=CheckoutStageSchema.choices(),
        default=CheckoutStageSchema.CREATED.value,  # Аналог Enum по строковому значению
        verbose_name="Описательный статус корзины",
        help_text="""
            CREATED - корзина создана, IN_PROGRESS - на корзину зарегистрировали заявку
        """,
    )
    basket_items = models.JSONField(null=True, blank=True, default=list)  # JSON аналог
    gift_items = models.JSONField(null=True, blank=True, default=list)  # JSON аналог

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"
        db_table = "baskets"
        managed = False

    def __str__(self):
        return f"Корзина id={self.id}, uuid_id={self.uuid_id}"

    def __repr__(self):
        return self.__str__()


# Перечисления
class PaymentType(models.TextChoices):
    ONLINE = "ONLINE", _("ONLINE")
    OFFLINE = "OFFLINE", _("OFFLINE")


class OrderStatusType(models.TextChoices):
    NEW = "NEW", _("NEW")
    INWORK = "INWORK", _("INWORK")
    COMPLETED = "COMPLITED", _("COMPLITED")
    CANCELED = "CANCELED", _("CANCELED")


class PaymentStatus(models.TextChoices):
    PAID = "PAID", _("PAID")
    UNPAID = "UNPAID", _("UNPAID")


class DeliveryType(models.TextChoices):
    PICKUP = "PICKUP", _("PICKUP")
    DELIVERY = "DELIVERY", _("DELIVERY")


class Orders(models.Model):
    # ФИО пользователя
    user_full_name = models.CharField(
        max_length=255,
        verbose_name="ФИО пользователя",
        help_text="""
            ФИО, которые пользователь указал при оформлении заявки
        """,
    )
    # ID пользователя
    user_id = models.UUIDField(
        verbose_name="ИД пользователя",
        help_text="""
            ИД пользователя, авторизированного в системе
        """,
    )
    # Общая сумма заказа
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.0"),
        verbose_name="Общая сумма заявки",
        help_text="""
            Отображается общая сумма заявки по всем товарам с учетом скидки
        """,
    )
    # Номер счета для банка
    account_number = models.IntegerField(
        unique=True,
        default=generate_account_number,
        verbose_name="ИД платежа",
        help_text="""
        Псевдослучайное, уникальное значение, которым отмечаем банкосвскую транзакцию
    """,
    )
    # Тип оплаты
    payment_type = models.CharField(
        max_length=20,
        choices=PaymentType.choices,
        default=PaymentType.ONLINE,
        verbose_name="Тип оплаты",
        help_text="""
            ONLINE - проведение платежа онлайн в системе по карте, OFFLINE - при получении товара
        """,
    )
    # Связь с корзиной
    uuid_id = models.ForeignKey(
        "Baskets",
        to_field="uuid_id",
        db_column="uuid_id",
        on_delete=models.CASCADE,
        unique=True,
        verbose_name="Корзина заявки",
        help_text="""
            Ссылка-указатель на корзину пользователя
        """,
    )
    # Статус заказа
    order_status = models.CharField(
        max_length=20,
        choices=OrderStatusType.choices,
        default=OrderStatusType.NEW,
        verbose_name="Статус заявки",
        help_text="""
            NEW - только создана пользователем, INWORK - принята в обработку менеджером,
            COMPLETED - заявка закрыта, CANCELED - заявка отменена
        """,
    )
    # Статус платежа
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.UNPAID,
        verbose_name="Статус оплаты заявки",
        help_text="""
            PAID - заявка оплачена, UNPAID - заявка не оплачена
        """,
    )
    # Комментарий к заказу
    comment = models.TextField(
        null=True,
        blank=True,
        verbose_name="Комментарий к заявке",
        help_text="""
        Тут пользователь может разместить комментарий к заявке при оформлении
    """,
    )
    # Номер телефона
    phone_number = models.CharField(
        max_length=20,
        verbose_name="Телефонный номер пользователя",
        help_text="""
            Контактный номер телефона для связи с пользователем
        """,
    )
    # Email
    email = models.EmailField(
        null=True,
        blank=True,
        verbose_name="Почтовый ящик ползователя",
        help_text="""
            Почтовый ящик на который отправлена ссылка для оплаты (в случае онлайн платеа)
        """,
    )
    # Город доставки
    shipping_city = models.CharField(
        max_length=255,
        verbose_name="Город доставки",
        help_text="""
            Город доставки указанный пользователем при оформлении заявки
        """,
    )
    # Адрес доставки
    delivery_address = models.TextField(
        null=True,
        blank=True,
        verbose_name="Адрес доставки",
        help_text="""
            Адрес доставки указанный пользователем при оформлении заявки
        """,
    )
    # Тип доставки
    delivery_type = models.CharField(
        max_length=20,
        choices=DeliveryType.choices,
        default=DeliveryType.DELIVERY,
        verbose_name="Тип доставки",
        help_text="""
            DELIVERY - силами продовца, PICKUP - самовывоз
        """,
    )
    # Менеджер, ответственный за выполнение заказа
    manager_executive = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        verbose_name="Менеджер исполнитель",
        help_text="Пользователь, принявший заявку в работу",
    )

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        db_table = "orders"
        managed = False

    def __str__(self):
        return f"Заявка № {self.pk} ({self.user_full_name})"
