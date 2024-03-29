# Generated by Django 3.2 on 2021-11-14 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0002_alter_place_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='lat',
            field=models.FloatField(blank=True, null=True, verbose_name='Широта'),
        ),
        migrations.AlterField(
            model_name='place',
            name='lon',
            field=models.FloatField(blank=True, null=True, verbose_name='Долгота'),
        ),
    ]
