from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from localflavor.generic.models import IBANField

from reports.constants import CURRENCIES
from reports.validators import card_validator


class Payment(models.Model):

    created_at = models.DateTimeField()
    currency = models.CharField(max_length=3, choices=CURRENCIES, default=None)
    amount = models.PositiveIntegerField(
        help_text="In units of currency's denomination"
    )
    description = models.TextField(max_length=300)


class PayByLink(Payment):
    bank = models.CharField(max_length=256)


class DirectPayment(Payment):
    iban = IBANField()


class Card(Payment):
    cardholder_name = models.CharField(max_length=256)
    cardholder_surname = models.CharField(max_length=256)
    card_number = models.CharField(max_length=16, validators=[card_validator])


class Report(models.Model):
    report = models.JSONField(encoder=DjangoJSONEncoder)
