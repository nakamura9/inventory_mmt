from django.conf.urls import url
import views as jc_views

app_name = "jobcards"


workorder_urls = [
    url(r"^new-work-order/?$", jc_views.NewWorkOrderView.as_view(), name="new-work-order"),
    url(r"^work-order-list/?$", jc_views.WorkOrderList.as_view(), name="work-order-list"),
    url(r"^complete-work-order/(?P<pk>[\w]+)/?$", jc_views.CompleteWorkOrderView.as_view(), name="complete-work-order"),
    url(r"^edit-work-order/(?P<pk>[\w]+)/?$", jc_views.EditNewWorkOrderView.as_view(), name="edit-work-order"),
    url(r'^accept-job/?$', jc_views.accept_job, name="accept-job"),
    url(r'^work-order-detail/(?P<pk>[\w]+)/?$', jc_views.WorkOrderDetailView.as_view(), name="work-order-detail"),
    url(r'^approve-job/(?P<pk>[\w ]+)$', jc_views.approve_job, name="approve-job"),
    url(r'^decline-job$', jc_views.decline_job, name="decline-job" ),
    url(r'^transfer-job/?$', jc_views.transfer_job, name="transfer-job")
]
preventative_task_urls = [
    url(r"^new-preventative-task/?$", jc_views.NewPreventativeTaskView.as_view(), name="new-preventative-task"),
    url(r"^complete-preventative-task/(?P<pk>[\w]+)/?$", jc_views.CompletePreventativeTaskView.as_view(), name="complete-preventative-task"),
    url(r"^edit-preventative-task/(?P<pk>[\w]+)/?$", jc_views.EditNewPreventativeTaskView.as_view(), name="edit-preventative-task"),
    url(r"^preventative-task-detail/(?P<pk>[\w]+)/?$", jc_views.PreventativeTaskDetailView.as_view(), name="preventative-task-detail"),
    url(r'^delete-preventative-task/(?P<pk>[\w]+)/?$', jc_views.delete_preventative_task, name="delete-preventative-task"),
]


urlpatterns = [
    url(r"^get_resolvers/?$", jc_views.get_resolvers, name="get_resolvers"),
] + workorder_urls + preventative_task_urls         