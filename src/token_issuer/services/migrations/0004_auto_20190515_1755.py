# Generated by Django 2.1.3 on 2019-05-15 15:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("zgw_consumers", "0003_auto_20190514_1009"),
        ("services", "0003_migrate_to_zgw_consumers"),
    ]

    operations = [
        migrations.RemoveField(model_name="configuration", name="ztcs",),
        migrations.AddField(
            model_name="configuration",
            name="primary_ac",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="zgw_consumers.Service",
                verbose_name="Authorization component (AC)",
            ),
        ),
    ]
