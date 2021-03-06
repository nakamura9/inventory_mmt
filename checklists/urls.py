from django.conf.urls import url

from . import views as ch_views

app_name = "checklists"

urlpatterns = [   
    url(r'^create_checklist/?$', ch_views.ChecklistCreateView.as_view(),
    name="create_checklist"),
    url(r'^complete_checklist/(?P<pk>[\w ]+)/?$', ch_views.ChecklistCompleteView.as_view(),
    name="complete_checklist"),
    url(r'^checklist_details/(?P<pk>[\w ]+)/?$', ch_views.ChecklistDetailView.as_view(),
    name="checklist_details"),
    url(r'^update_checklist/(?P<pk>[\w ]+)/?$', ch_views.ChecklistUpdateView.as_view(),
    name="update_checklist"),
    url(r'^delete_checklist/(?P<pk>[\w ]+)/?$', ch_views.delete_checklist,
    name="delete_checklist"),
    url(r'^hold_checklist/(?P<pk>[\w ]+)/??$', ch_views.hold_checklist,
    name="hold_checklist"),
]