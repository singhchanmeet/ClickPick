# Generated by Django 5.0 on 2024-01-27 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stationery', '0002_alter_activeorders_quantity_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activeorders',
            name='custom_message',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='activeprintouts',
            name='custom_message',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='pastorders',
            name='custom_message',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='pastprintouts',
            name='custom_message',
            field=models.TextField(blank=True),
        ),
    ]
