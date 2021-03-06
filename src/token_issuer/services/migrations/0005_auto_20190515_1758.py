# Generated by Django 2.1.3 on 2019-05-15 15:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("services", "0004_auto_20190515_1755"),
    ]

    operations = [
        migrations.AlterField(
            model_name="configuration",
            name="primary_ac",
            field=models.ForeignKey(
                limit_choices_to={"api_type": "ac"},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="zgw_consumers.Service",
                verbose_name="Authorization component (AC)",
            ),
        ),
    ]
