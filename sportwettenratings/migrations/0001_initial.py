# Generated by Django 2.2.5 on 2022-03-24 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('code2', models.CharField(max_length=16)),
                ('code3', models.CharField(max_length=16)),
                ('flag', models.CharField(max_length=256)),
                ('slug', models.CharField(max_length=64, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]