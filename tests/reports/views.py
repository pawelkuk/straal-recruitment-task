from collections import namedtuple

import pytest
import requests
from rest_framework.test import APIClient

from reports.models import Report

EXCHANGE_RATE = 2


@pytest.fixture(autouse=True)
def monkeypatch_requests(monkeypatch):
    class MockResponse:
        status_code = 200

        @staticmethod
        def json():
            return {"rates": [{"mid": EXCHANGE_RATE}]}

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)


TestData = namedtuple("TestData", ["request_body", "expected_response"])


class TestReportView:
    @pytest.mark.parametrize(
        "data",
        [
            TestData(
                request_body={
                    "pay_by_link": [
                        {
                            "created_at": "2021-05-13T01:01:43-08:00",
                            "currency": "EUR",
                            "amount": 3000,
                            "description": "Abonament na siłownię",
                            "bank": "mbank",
                        }
                    ],
                },
                expected_response=[
                    {
                        "date": "2021-05-13T09:01:43Z",
                        "type": "pay_by_link",
                        "payment_mean": "mbank",
                        "description": "Abonament na siłownię",
                        "currency": "EUR",
                        "amount": 3000,
                        "amount_in_pln": EXCHANGE_RATE * 3000,
                    },
                ],
            ),
            TestData(
                request_body={
                    "dp": [
                        {
                            "created_at": "2021-05-14T08:27:09Z",
                            "currency": "USD",
                            "amount": 599,
                            "description": "FastFood",
                            "iban": "DE91100000000123456789",
                        }
                    ],
                },
                expected_response=[
                    {
                        "date": "2021-05-14T08:27:09Z",
                        "type": "dp",
                        "payment_mean": "DE91100000000123456789",
                        "description": "FastFood",
                        "currency": "USD",
                        "amount": 599,
                        "amount_in_pln": 599 * EXCHANGE_RATE,
                    },
                ],
            ),
            TestData(
                request_body={
                    "card": [
                        {
                            "created_at": "2021-05-13T09:00:05+02:00",
                            "currency": "PLN",
                            "amount": 2450,
                            "description": "REF123457",
                            "cardholder_name": "John",
                            "cardholder_surname": "Doe",
                            "card_number": "341111111111111",
                        },
                    ]
                },
                expected_response=[
                    {
                        "date": "2021-05-13T07:00:05Z",
                        "type": "card",
                        "payment_mean": "John None 3411*******1111",
                        "description": "REF123457",
                        "currency": "PLN",
                        "amount": 2450,
                        "amount_in_pln": 2450,
                    },
                ],
            ),
            TestData(
                request_body={
                    "card": [
                        {
                            "created_at": "2021-05-14T18:32:26Z",
                            "currency": "GBP",
                            "amount": 1000,
                            "description": "REF123456",
                            "cardholder_name": "John",
                            "cardholder_surname": "Doe",
                            "card_number": "378282246310005",
                        }
                    ]
                },
                expected_response=[
                    {
                        "date": "2021-05-14T18:32:26Z",
                        "type": "card",
                        "payment_mean": "John None 3782*******0005",
                        "description": "REF123456",
                        "currency": "GBP",
                        "amount": 1000,
                        "amount_in_pln": 1000 * EXCHANGE_RATE,
                    }
                ],
            ),
        ],
    )
    def test_report_view_returns_valid_report_for_single_payment_record(self, data):
        client = APIClient()
        response = client.post(
            "/report/",
            data.request_body,
            format="json",
        )
        assert response.status_code == 200
        assert response.json() == data.expected_response

    @pytest.mark.parametrize(
        "data",
        [
            TestData(
                request_body={
                    "pay_by_link": [
                        {
                            "created_at": "2021-05-13T01:01:43-08:00",
                            "currency": "ABC",
                            "amount": 3000,
                            "description": "Abonament na siłownię",
                            "bank": "mbank",
                        }
                    ],
                },
                expected_response=[{"currency": ['"ABC" is not a valid choice.']}],
            ),
            TestData(
                request_body={
                    "pay_by_link": [
                        {
                            "created_at": "2021-05-13",
                            "currency": "USD",
                            "amount": 3000,
                            "description": "Abonament na siłownię",
                            "bank": "mbank",
                        }
                    ],
                },
                expected_response=[
                    {
                        "created_at": [
                            "Datetime has wrong format. Use one of these formats instead: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z]."
                        ]
                    }
                ],
            ),
            TestData(
                request_body={
                    "pay_by_link": [
                        {
                            "created_at": "2021-05-13T01:01:43-08:00",
                            "currency": "USD",
                            "amount": -1,
                            "description": "Abonament na siłownię",
                            "bank": "mbank",
                        }
                    ],
                },
                expected_response=[
                    {"amount": ["Ensure this value is greater than or equal to 0."]}
                ],
            ),
            TestData(
                request_body={
                    "pay_by_link": [
                        {
                            "created_at": "2021-05-13T01:01:43-08:00",
                            "currency": "USD",
                            "amount": 3000,
                            "description": "",
                            "bank": "mbank",
                        }
                    ],
                },
                expected_response=[{"description": ["This field may not be blank."]}],
            ),
            TestData(
                request_body={
                    "pay_by_link": [
                        {
                            "created_at": None,
                            "currency": None,
                            "amount": None,
                            "description": "",
                            "bank": "",
                        }
                    ],
                },
                expected_response=[
                    {
                        "created_at": ["This field may not be null."],
                        "description": ["This field may not be blank."],
                        "currency": ["This field may not be null."],
                        "amount": ["This field may not be null."],
                        "bank": ["This field may not be blank."],
                    }
                ],
            ),
        ],
    )
    def test_report_returns_bad_request_with_errors_for_invalid_data(self, data):
        client = APIClient()
        response = client.post(
            "/report/",
            data.request_body,
            format="json",
        )
        assert response.status_code == 400
        assert response.json() == data.expected_response

    def test_response_returns_report_in_chronological_order(self):
        client = APIClient()
        response = client.post(
            "/report/",
            {
                "pay_by_link": [
                    {
                        "created_at": "2021-05-13T01:01:43-08:00",
                        "currency": "EUR",
                        "amount": 3000,
                        "description": "Abonament na siłownię",
                        "bank": "mbank",
                    }
                ],
                "dp": [
                    {
                        "created_at": "2021-05-14T08:27:09Z",
                        "currency": "USD",
                        "amount": 599,
                        "description": "FastFood",
                        "iban": "DE91100000000123456789",
                    }
                ],
                "card": [
                    {
                        "created_at": "2021-05-13T09:00:05+02:00",
                        "currency": "PLN",
                        "amount": 2450,
                        "description": "REF123457",
                        "cardholder_name": "John",
                        "cardholder_surname": "Doe",
                        "card_number": "341111111111111",
                    },
                    {
                        "created_at": "2021-05-14T18:32:26Z",
                        "currency": "GBP",
                        "amount": 1000,
                        "description": "REF123456",
                        "cardholder_name": "John",
                        "cardholder_surname": "Doe",
                        "card_number": "378282246310005",
                    },
                ],
            },
            format="json",
        )
        assert response.status_code == 200
        assert response.json() == [
            {
                "date": "2021-05-13T07:00:05Z",
                "type": "card",
                "payment_mean": "John None 3411*******1111",
                "description": "REF123457",
                "currency": "PLN",
                "amount": 2450,
                "amount_in_pln": 2450,
            },
            {
                "date": "2021-05-13T09:01:43Z",
                "type": "pay_by_link",
                "payment_mean": "mbank",
                "description": "Abonament na siłownię",
                "currency": "EUR",
                "amount": 3000,
                "amount_in_pln": 3000 * EXCHANGE_RATE,
            },
            {
                "date": "2021-05-14T08:27:09Z",
                "type": "dp",
                "payment_mean": "DE91100000000123456789",
                "description": "FastFood",
                "currency": "USD",
                "amount": 599,
                "amount_in_pln": 599 * EXCHANGE_RATE,
            },
            {
                "date": "2021-05-14T18:32:26Z",
                "type": "card",
                "payment_mean": "John None 3782*******0005",
                "description": "REF123456",
                "currency": "GBP",
                "amount": 1000,
                "amount_in_pln": 1000 * EXCHANGE_RATE,
            },
        ]


@pytest.mark.django_db
class TestCustomerReport:
    def test_customer_report_saved_in_database(
        self,
    ):
        client = APIClient()
        response = client.post(
            "/customer-report/",
            {
                "pay_by_link": [
                    {
                        "created_at": "2021-05-13T01:01:43-08:00",
                        "currency": "EUR",
                        "amount": 3001,
                        "description": "Abonament na siłownię",
                        "bank": "mbank",
                    }
                ],
            },
            format="json",
        )
        assert response.status_code == 201
        customer_id = response.json().get("customer_id")
        report = Report.objects.get(id=customer_id)
        get_response = client.get(f"/customer-report/{customer_id}/")
        assert (
            report.report
            == get_response.json()
            == [
                {
                    "date": "2021-05-13T09:01:43Z",
                    "type": "pay_by_link",
                    "amount": 3001,
                    "currency": "EUR",
                    "description": "Abonament na siłownię",
                    "payment_mean": "mbank",
                    "amount_in_pln": 3001 * EXCHANGE_RATE,
                }
            ]
        )

    def test_customer_report_updates_existing_report(self):
        client = APIClient()
        # Given an existing report
        response = client.post(
            "/customer-report/",
            {
                "pay_by_link": [
                    {
                        "created_at": "2021-05-13T01:01:43-08:00",
                        "currency": "EUR",
                        "amount": 3001,
                        "description": "Abonament na siłownię",
                        "bank": "mbank",
                    }
                ],
            },
            format="json",
        )
        assert response.status_code == 201
        customer_id = response.json().get("customer_id")
        # Update the created report by passgin customer_id obtaned in first response
        response = client.post(
            "/customer-report/",
            {
                "customer_id": customer_id,
                "pay_by_link": [
                    {
                        "created_at": "2021-05-13T01:01:43-08:00",
                        "currency": "EUR",
                        "amount": 9999,
                        "description": "Abonament na jogę",
                        "bank": "pko",
                    }
                ],
            },
            format="json",
        )
        assert response.status_code == 201
        report = Report.objects.get(id=customer_id)
        # Assert report is updated
        get_response = client.get(f"/customer-report/{customer_id}/")
        assert (
            report.report
            == get_response.json()
            == [
                {
                    "date": "2021-05-13T09:01:43Z",
                    "type": "pay_by_link",
                    "amount": 9999,
                    "currency": "EUR",
                    "description": "Abonament na jogę",
                    "payment_mean": "pko",
                    "amount_in_pln": 9999 * EXCHANGE_RATE,
                }
            ]
        )
