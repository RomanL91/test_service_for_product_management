# Generated by Django 5.0.6 on 2025-05-05 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app_category", "0001_initial"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="category",
            index=models.Index(fields=["slug"], name="app_categor_slug_4b2c6d_idx"),
        ),
        migrations.AddIndex(
            model_name="category",
            index=models.Index(
                fields=["name_category"], name="app_categor_name_ca_b893f4_idx"
            ),
        ),
    ]
