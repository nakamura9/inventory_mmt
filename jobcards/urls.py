from django.conf.urls import url
import views as jc_views

app_name = "jobcards"


workorder_urls = [
    url(r"^new-work-order/?$", jc_views.NewWorkOrderView.as_view(), name="new-work-order"),
    url(r"^work-order-list/?$", jc_views.WorkOrderList.as_view(), name="work-order-list"),
    url(r"^complete-work-order/(?P<pk>[\w]+)/?$", jc_views.CompleteWorkOrderView.as_view(), name="complete-work-order"),
    url(r"^edit-work-order/(?P<pk>[\w]+)/?$", jc_views.EditNewWorkOrderView.as_view(), name="edit-work-order"),
]
preventative_task_urls = [
    url(r"^new-preventative-task/?$", jc_views.NewPreventativeTaskView.as_view(), name="new-preventative-task"),
    url(r"^complete-preventative-task/(?P<pk>[\w]+)/?$", jc_views.CompletePreventativeTaskView.as_view(), name="complete-preventative-task"),
    url(r"^edit-preventative-task/(?P<pk>[\w]+)/?$", jc_views.EditNewPreventativeTaskView.as_view(), name="edit-preventative-task"),
]


urlpatterns = [
    url(r"^get_resolvers/?$", jc_views.get_resolvers, name="get_resolvers"),
] + workorder_urls + preventative_task_urls         