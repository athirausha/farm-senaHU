# Generated by Django 3.0.7 on 2020-06-15 08:14

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Base',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('base_name', models.CharField(default='Nothing', max_length=300)),
                ('base_create_date', models.DateField(default=django.utils.timezone.now)),
                ('base_modified_date', models.DateField(default=django.utils.timezone.now)),
                ('created_by', models.CharField(default='Nothing', max_length=300)),
                ('technical_name', models.CharField(default='Nothing', max_length=300)),
                ('table_type', models.CharField(default='Nothing', max_length=300)),
                ('discription', models.CharField(default='Nothing', max_length=500)),
                ('purpose', models.CharField(default='Nothing', max_length=400)),
                ('bcp', models.CharField(default='Nothing', max_length=300)),
                ('tags', models.CharField(default='Nothing', max_length=400)),
                ('fk', models.IntegerField(default=1)),
            ],
            options={
                'db_table': 'Base',
            },
        ),
        migrations.CreateModel(
            name='Basecolumns',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('base_name', models.CharField(default='Nothing', max_length=300)),
                ('base_create_date', models.DateField(default=django.utils.timezone.now)),
                ('base_modified_date', models.DateField(default=django.utils.timezone.now)),
                ('c_name', models.CharField(default='Nothing', max_length=300)),
                ('d_type', models.CharField(default='Text', max_length=300)),
                ('base_fk', models.IntegerField(default=1)),
            ],
            options={
                'db_table': 'Basecolumns',
            },
        ),
        migrations.CreateModel(
            name='Login',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Nothing', max_length=50)),
                ('phone', models.CharField(default='Nothing', max_length=50)),
                ('password', models.CharField(default='Nothing', max_length=50)),
                ('email', models.CharField(default='Nothing', max_length=50)),
                ('is_active', models.CharField(default='Nothing', max_length=50)),
            ],
            options={
                'db_table': 'Login',
            },
        ),
    ]
