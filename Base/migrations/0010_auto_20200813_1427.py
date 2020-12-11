# Generated by Django 3.0.7 on 2020-08-13 08:57

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Base', '0009_auto_20200731_1155'),
    ]

    operations = [
        migrations.AddField(
            model_name='login',
            name='account_type',
            field=models.CharField(default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='pdfreport',
            name='created_date',
            field=models.DateField(default=datetime.date(2020, 8, 13)),
        ),
        migrations.AlterField(
            model_name='report',
            name='created_date',
            field=models.DateField(default=datetime.date(2020, 8, 13)),
        ),
        migrations.AlterField(
            model_name='user_list',
            name='created_date',
            field=models.DateField(default=datetime.date(2020, 8, 13)),
        ),
    ]
