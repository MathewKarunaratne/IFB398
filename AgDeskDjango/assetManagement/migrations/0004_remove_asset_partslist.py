# Generated by Django 5.0.4 on 2024-10-13 06:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("assetManagement", "0003_assetpart"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="asset",
            name="partsList",
        ),
    ]
