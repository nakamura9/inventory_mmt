from django.conf.urls import url
import views as ch_views

app_name = "checklists"

urlpatterns = [
    
    url(r'^inbox/?$', ch_views.ChecklistListView.as_view(),
    name="inbox"),
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
    url(r'^add_task/?$', ch_views.add_task,
    name="add_task"),
    url(r'^hold_checklist/(?P<pk>[\w ]+)/??$', ch_views.hold_checklist,
    name="hold_checklist"),
    url(r'^remove_task/?$', ch_views.remove_task,
    name="remove_task"),

   
]