# Generated by Django 4.1.1 on 2022-10-20 02:01

from django.db import migrations, models
import project.storages_backends


class Migration(migrations.Migration):

    dependencies = [
        ("customers", "0002_customer_photo_alter_customer_blowing_direction_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customer",
            name="photo",
            field=models.ImageField(
                blank=True,
                null=True,
                storage=project.storages_backends.PrivateMediaStorage(),
                upload_to="",
            ),
        ),
    ]
