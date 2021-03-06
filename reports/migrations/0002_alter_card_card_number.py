# Generated by Django 3.2.3 on 2021-05-17 18:11

from django.db import migrations, models

import reports.validators


class Migration(migrations.Migration):

    dependencies = [
        ("reports", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="card",
            name="card_number",
            field=models.CharField(
                max_length=16, validators=[reports.validators.card_validator]
            ),
        ),
    ]
