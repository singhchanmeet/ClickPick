# Generated by Django 4.2.6 on 2024-02-03 15:28

from django.db import migrations, models
import stationery.utils


class Migration(migrations.Migration):

    dependencies = [
        ('stationery', '0005_delete_tempfilestorage'),
    ]

    operations = [
        migrations.CreateModel(
            name='TempFileStorage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=stationery.utils.temp_file_rename)),
            ],
        ),
    ]