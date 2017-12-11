from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^$', ReportingHome.as_view(),name="home" ),
    url(r"^wizard/?$", ReportWizard.as_view(), name="wizard"),
    url(r'^report-selection/$', ReportSelection.as_view(), name= "report-selection"),
    url(r'^maintenance-report/(?P<pk>[\d]+)$', MaintenanceReport.as_view(), name="maintenance-report"),
    url(r'^maintenance-report-form/$', MaintenanceReportForm.as_view(), name="maintenance-report-form"),
    url(r"^delete-report/(?P<pk>[\w]+)/$", delete_report, name="delete-report"),
]