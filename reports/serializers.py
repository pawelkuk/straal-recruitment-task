import logging
from typing import OrderedDict

from django.core.serializers.json import DjangoJSONEncoder
from rest_framework import serializers
from rest_framework.fields import JSONField

from reports.integration import get_exchange_rate
from reports.models import Card, DirectPayment, PayByLink, Payment, Report
from reports.utils import mask_card_number


class PaymentSerializer(serializers.ModelSerializer):
    amount_in_pln = serializers.SerializerMethodField()
    payment_mean = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()

    # Specifies the subset of field which will be returned in to_representation
    return_fields = (
        "date",
        "currency",
        "amount",
        "description",
        "amount_in_pln",
        "payment_mean",
        "type",
    )

    class Meta:
        model = Payment
        fields = (
            "created_at",
            "date",
            "type",
            "payment_mean",
            "description",
            "currency",
            "amount",
            "amount_in_pln",
        )

    def get_amount_in_pln(self, obj):
        currency = obj.get("currency")
        date = obj.get("created_at")
        try:
            exchange_rate = get_exchange_rate(currency, date)
        except Exception as e:
            logging.exception(e)
            return None
        return int(obj.get("amount") * exchange_rate)

    def to_representation(self, instance):
        """Filters out fields which are not present in self.return_fields"""
        ret = super().to_representation(instance)
        return OrderedDict(
            [(key, val) for key, val in ret.items() if key in self.return_fields]
        )

    def get_type(self, obj):
        return self.payment_type

    def get_date(self, obj):
        return obj.get("created_at")


class DirectPaymentSerializer(PaymentSerializer):
    payment_type = "dp"

    class Meta:
        model = DirectPayment
        fields = PaymentSerializer.Meta.fields + ("iban",)

    def get_payment_mean(self, obj):
        return obj.get("iban")


class CardPaymentSerializer(PaymentSerializer):
    payment_type = "card"

    class Meta:
        model = Card
        fields = PaymentSerializer.Meta.fields + (
            "cardholder_name",
            "cardholder_surname",
            "card_number",
        )

    def get_payment_mean(self, obj):
        card_number = obj.get("card_number")
        masked_card_number = mask_card_number(card_number)
        return (
            f"{obj.get('cardholder_name')} "
            f"{obj.get('cardholder_surnamename')} "
            f"{masked_card_number}"
        )


class ByLinkPaymentSerializer(PaymentSerializer):
    payment_type = "pay_by_link"

    class Meta:
        model = PayByLink
        fields = PaymentSerializer.Meta.fields + ("bank",)

    def get_payment_mean(self, obj):
        return obj.get("bank")


class ReportSerializer(serializers.ModelSerializer):
    report = JSONField(encoder=DjangoJSONEncoder)

    class Meta:
        model = Report
        fields = ["report"]
