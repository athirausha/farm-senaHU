# Generated by Django 3.0.7 on 2020-09-10 17:00

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Base', '0015_auto_20200827_1936'),
    ]

    operations = [
        migrations.AddField(
            model_name='login',
            name='disable_period_end',
            field=models.CharField(default='Unknown', max_length=300),
        ),
        migrations.AlterField(
            model_name='pdfreport',
            name='created_date',
            field=models.DateField(default=datetime.date(2020, 9, 10)),
        ),
        migrations.AlterField(
            model_name='report',
            name='created_date',
            field=models.DateField(default=datetime.date(2020, 9, 10)),
        ),
        migrations.AlterField(
            model_name='user_list',
            name='created_date',
            field=models.DateField(default=datetime.date(2020, 9, 10)),
        ),
    ]
