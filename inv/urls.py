from django.conf.urls import url
import views


urlpatterns = [
    url(r'^browse$', views.PlantView.as_view(), name="browse"),
    url(r'^component_details/(?P<pk>[ -~]+)/?$', views.ComponentView.as_view(), name="component_details"),
    url(r'^subunit_details/(?P<pk>[ -~]+)/?$', views.SubUnitView.as_view(), name="subunit_details"),
    url(r'^subassembly_details/(?P<pk>[ -~]+)/?$', views.SubAssyView.as_view(), name="subassembly_details"),
    url(r'^machine_details/(?P<pk>[ -~]+)/?$', views.MachineView.as_view(), name="machine_details"),
    url(r'^planned_maintenance/?$', views.MaintenanceView.as_view(), name="planned_maintenance"),
    url(r'^inv-home/?$', views.invHome.as_view(), name="inv-home"),
]