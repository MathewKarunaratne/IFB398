# Generated by Django 5.0.4 on 2024-09-24 09:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('FarmAcc', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='asset',
            fields=[
                ('assetPrefix', models.CharField(max_length=2)),
                ('assetID', models.AutoField(primary_key=True, serialize=False)),
                ('assetName', models.CharField(max_length=100)),
                ('Manufacturer', models.CharField(max_length=100)),
                ('partsList', models.CharField(max_length=255)),
                ('Location', models.CharField(max_length=100)),
                ('dateManufactured', models.DateField()),
                ('datePurchased', models.DateField()),
                ('deleted', models.BooleanField(default=False)),
                ('assetImage', models.ImageField(default='images/asset_images/defaultImage.jpg', upload_to='images/asset_images')),
                ('farmID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='FarmAcc.farminfo')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_%(app_label)s.%(class)s_set+', to='contenttypes.contenttype')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
        ),
        migrations.CreateModel(
            name='heavyVehicle',
            fields=[
                ('asset_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='assetManagement.asset')),
                ('vin', models.CharField(max_length=100)),
                ('Registration', models.CharField(max_length=100)),
                ('inTransport', models.BooleanField()),
                ('interFarmTransport', models.BooleanField()),
            ],
            options={
                'abstract': False,
            },
            bases=('assetManagement.asset',),
        ),
        migrations.CreateModel(
            name='LargeEquipment',
            fields=[
                ('asset_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='assetManagement.asset')),
                ('vin', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('assetManagement.asset',),
        ),
        migrations.CreateModel(
            name='lightVehicle',
            fields=[
                ('asset_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='assetManagement.asset')),
                ('vin', models.CharField(max_length=100)),
                ('Registration', models.CharField(max_length=100)),
                ('currentlyInUse', models.BooleanField()),
            ],
            options={
                'abstract': False,
            },
            bases=('assetManagement.asset',),
        ),
        migrations.CreateModel(
            name='SmallEquipment',
            fields=[
                ('asset_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='assetManagement.asset')),
                ('serialNumber', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('assetManagement.asset',),
        ),
    ]
