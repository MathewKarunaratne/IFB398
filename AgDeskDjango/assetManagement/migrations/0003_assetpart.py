# Generated by Django 5.0.4 on 2024-10-13 06:10

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("assetManagement", "0002_asset_usageminutes"),
    ]

    operations = [
        migrations.CreateModel(
            name="AssetPart",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "part_name",
                    models.CharField(max_length=100, verbose_name="Part Name"),
                ),
                (
                    "hours_before_maintenance",
                    models.PositiveIntegerField(
                        verbose_name="Hours Before Maintenance"
                    ),
                ),
                (
                    "asset",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="parts",
                        to="assetManagement.asset",
                    ),
                ),
            ],
        ),
    ]
