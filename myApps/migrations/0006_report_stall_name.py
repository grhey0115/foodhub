# Generated by Django 5.1.1 on 2025-01-07 03:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApps', '0005_remove_admin_otp_remove_admin_otp_expiration'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='stall_name',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='myApps.stall'),
        ),
    ]
