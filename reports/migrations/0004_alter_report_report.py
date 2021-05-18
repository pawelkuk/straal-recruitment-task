# Generated by Django 3.2.3 on 2021-05-18 21:52

import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reports", "0003_report"),
    ]

    operations = [
        migrations.AlterField(
            model_name="report",
            name="report",
            field=models.JSONField(
                encoder=django.core.serializers.json.DjangoJSONEncoder
            ),
        ),
    ]