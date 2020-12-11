# Generated by Django 3.0.7 on 2020-07-30 03:59

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Base', '0006_auto_20200723_1257'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Reportname', models.CharField(default='Nothing', max_length=50)),
                ('DetailRname', models.CharField(default='Nothing', max_length=50)),
                ('table_id', models.IntegerField(default=0)),
                ('created_date', models.DateField(default=datetime.date(2020, 7, 30))),
                ('created_by', models.CharField(default='Nothing', max_length=300)),
            ],
            options={
                'db_table': 'report',
            },
        ),
        migrations.CreateModel(
            name='Reportcontent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reportid', models.IntegerField(default=0)),
                ('column_id', models.IntegerField(default=1)),
            ],
            options={
                'db_table': 'reportid',
            },
        ),
        migrations.AddField(
            model_name='calculation',
            name='const_position',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='calculation',
            name='type_of_calc',
            field=models.CharField(default='Normal_calc', max_length=100),
        ),
        migrations.AlterField(
            model_name='user_list',
            name='created_date',
            field=models.DateField(default=datetime.date(2020, 7, 30)),
        ),
    ]
