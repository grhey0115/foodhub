# Generated by Django 5.1.1 on 2025-01-09 11:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApps', '0009_remove_product_description_remove_product_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='item_name',
            field=models.ForeignKey(blank=True, db_column='item_name_id', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='myApps.fooditem'),
        ),
        migrations.AlterField(
            model_name='product',
            name='stall_name',
            field=models.ForeignKey(blank=True, db_column='stall_name_id', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='myApps.stall'),
        ),
    ]
