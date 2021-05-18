from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from reports.models import Report

from .serializers import (
    ByLinkPaymentSerializer,
    CardPaymentSerializer,
    DirectPaymentSerializer,
    ReportSerializer,
)


def generate_report(data):
    report, errors = [], []
    if direct_payments := data.get("dp"):
        for direct_payment in direct_payments:
            serializer = DirectPaymentSerializer(data=direct_payment)
            if serializer.is_valid():
                report.append(serializer)
            else:
                errors.append(serializer.errors)
    if card_payments := data.get("card"):
        for card_payment in card_payments:
            serializer = CardPaymentSerializer(data=card_payment)
            if serializer.is_valid():
                report.append(serializer)
            else:
                errors.append(serializer.errors)
    if by_link_payments := data.get("pay_by_link"):
        for by_link_payment in by_link_payments:
            serializer = ByLinkPaymentSerializer(data=by_link_payment)
            if serializer.is_valid():
                report.append(serializer)
            else:
                errors.append(serializer.errors)
    return report, errors


class ReportView(APIView):
    def post(self, request: Request):
        data = request.data

        report, errors = generate_report(data)
        if errors:
            return Response(errors, status=400)

        report = sorted(
            report, key=lambda payment: payment.validated_data.get("created_at")
        )
        report = [serializer.data for serializer in report]
        return Response(report, status=200)


class CustomerReportView(APIView):
    def post(self, request: Request):
        data = request.data
        customer_id = data.pop("customer_id", None)

        report, errors = generate_report(data)
        if errors:
            return Response(errors, status=400)

        report = sorted(
            report, key=lambda payment: payment.validated_data.get("created_at")
        )
        report = [serializer.data for serializer in report]

        try:
            instance = Report.objects.get(id=customer_id)
        except Report.DoesNotExist:
            instance = None

        report_serializer = ReportSerializer(instance, data={"report": report})
        if report_serializer.is_valid():
            customer_report = report_serializer.save()
        else:
            return Response(report_serializer.errors, status=400)

        return Response({"customer_id": customer_report.id}, status=201)

    def get(self, request: Request, customer_id=None):
        if not customer_id:
            return Response("Not found", status=404)

        try:
            report = Report.objects.get(id=customer_id)
        except Report.DoesNotExist:
            return Response("Not found", status=404)

        return Response(report.report, status=200)
