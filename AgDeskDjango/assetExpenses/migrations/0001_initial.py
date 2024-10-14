# Generated by Django 5.0.4 on 2024-09-24 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('expenseID', models.AutoField(primary_key=True, serialize=False)),
                ('expenseType', models.SmallIntegerField(choices=[(0, 'Fuel'), (1, 'Maintenance'), (2, 'Insurance'), (3, 'Registration'), (4, 'Other')], default=0)),
                ('cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('receiptNumber', models.PositiveIntegerField()),
                ('deleted', models.BooleanField(default=False)),
            ],
        ),
    ]
