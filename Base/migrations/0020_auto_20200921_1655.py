# Generated by Django 3.0.7 on 2020-09-21 11:25

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Base', '0019_auto_20200915_1705'),
    ]

    operations = [
        migrations.CreateModel(
            name='designation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile', models.CharField(default='No', max_length=50)),
                ('created_by', models.CharField(default='Nothing', max_length=300)),
            ],
            options={
                'db_table': 'designation',
            },
        ),
        migrations.AlterField(
            model_name='pdfreport',
            name='created_date',
            field=models.DateField(default=datetime.date(2020, 9, 21)),
        ),
        migrations.AlterField(
            model_name='report',
            name='created_date',
            field=models.DateField(default=datetime.date(2020, 9, 21)),
        ),
        migrations.AlterField(
            model_name='user_list',
            name='created_date',
            field=models.DateField(default=datetime.date(2020, 9, 21)),
        ),
    ]
