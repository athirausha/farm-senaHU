# Generated by Django 3.0.7 on 2020-09-15 11:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Base', '0018_basecolumns_nul_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pdfreport',
            name='created_date',
            field=models.DateField(default=datetime.date(2020, 9, 15)),
        ),
        migrations.AlterField(
            model_name='report',
            name='created_date',
            field=models.DateField(default=datetime.date(2020, 9, 15)),
        ),
        migrations.AlterField(
            model_name='user_list',
            name='created_date',
            field=models.DateField(default=datetime.date(2020, 9, 15)),
        ),
    ]