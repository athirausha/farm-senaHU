# Generated by Django 3.0.7 on 2020-10-07 09:38

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Base', '0020_auto_20200921_1655'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pdfreport',
            name='created_date',
            field=models.DateField(default=datetime.date(2020, 10, 7)),
        ),
        migrations.AlterField(
            model_name='report',
            name='created_date',
            field=models.DateField(default=datetime.date(2020, 10, 7)),
        ),
        migrations.AlterField(
            model_name='user_list',
            name='created_date',
            field=models.DateField(default=datetime.date(2020, 10, 7)),
        ),
    ]
