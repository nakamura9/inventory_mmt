from django.conf.urls import url
from .views import *
from .report_pdf_creator import generate_pdf

urlpatterns = [
    url(r'^$', ReportingHome.as_view(),name="home" ),
    url(r'^report-selection/$', ReportSelection.as_view(), name= "report-selection"),
    url(r'^report/(?P<pk>[\w ]+)/?$', ReportView.as_view(), name="report"),
    url(r'^report-form/(?P<type>[\w ]+)/$', ReportForm.as_view(), name="report-form"),
    url(r"^delete-report/(?P<pk>[\w]+)/$", delete_report, name="delete-report"),
    url(r'generate-pdf/(?P<pk>[\w ]+)/$', generate_pdf, name="generate-pdf"),
]