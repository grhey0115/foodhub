# Generated by Django 5.1.1 on 2025-01-09 10:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApps', '0008_rename_name_product_item_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='item_name',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='myApps.fooditem'),
        ),
    ]
