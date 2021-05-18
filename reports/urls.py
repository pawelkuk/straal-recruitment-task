from django.urls import path

from . import views

urlpatterns = [
    path("report/", views.ReportView.as_view()),
    path("customer-report/", views.CustomerReportView.as_view()),
    path("customer-report/<int:customer_id>/", views.CustomerReportView.as_view()),
]
