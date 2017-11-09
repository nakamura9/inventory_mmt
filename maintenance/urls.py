from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^inbox/?$', MaintenanceInbox.as_view(), name="inbox"),
    url(r'^machine-overview/?$', MachineOverView.as_view(), name="machine-overview"),
    url(r'^planned-maintenance/?$', PlannedMaintenanceView.as_view(), name="planned-maintenance"),
]