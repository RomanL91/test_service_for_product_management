# Generated by Django 5.0.6 on 2024-12-26 22:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app_orders", "0002_alter_baskets_options_alter_orders_options"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="baskets",
            options={
                "managed": False,
                "verbose_name": "Корзина",
                "verbose_name_plural": "Корзины",
            },
        ),
        migrations.AlterModelOptions(
            name="orders",
            options={
                "managed": False,
                "verbose_name": "Заявка",
                "verbose_name_plural": "Заявки",
            },
        ),
    ]
