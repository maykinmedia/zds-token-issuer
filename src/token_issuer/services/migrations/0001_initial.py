# Generated by Django 2.1.3 on 2018-11-15 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Service",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("label", models.CharField(max_length=100, verbose_name="label")),
                ("api_root", models.CharField(max_length=255, verbose_name="address")),
            ],
        ),
    ]
