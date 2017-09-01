from django.conf.urls import url
import views as jc_views

app_name = "jobcards"


workorder_urls = [
    url(r"^new-work-order/?$", jc_views.NewWorkOrderView.as_view(), name="new-work-order"),
    url(r"^complete-work-order/(?P<pk>[\w]+)/?$", jc_views.CompleteWorkOrderView.as_view(), name="complete-work-order"),
    url(r"^edit-work-order/(?P<pk>[\w]+)/?$", jc_views.EditNewWorkOrderView.as_view(), name="edit-work-order"),
]
preventative_task_urls = [
    url(r"^new-preventative-task/?$", jc_views.NewPreventativeTaskView.as_view(), name="new-preventative-task"),
    url(r"^complete-preventative-task/(?P<pk>[\w]+)/?$", jc_views.CompletePreventativeTaskView.as_view(), name="complete-preventative-task"),
]


urlpatterns = [
    url(r"^new_planned_job/?$", jc_views.NewPlannedJobView.as_view(), name="new_planned_job"),
    url(r"^edit_planned_job/(?P<pk>[\w]+)/?$", jc_views.EditPlannedJob.as_view(), name="edit_planned_job"),
    url(r"^delete_planned_job/(?P<pk>[\w]+)/?$", jc_views.delete_planned_job, name="delete_planned_job"),
    url(r"^new_unplanned_job/?$", jc_views.NewUnplannedJobView.as_view(), name="new_unplanned_job"),
    url(r"^edit_unplanned_job/(?P<pk>[\w]+)/?$", jc_views.EditUnPlannedJob.as_view(), name="edit_unplanned_job"),
    url(r"^delete_unplanned_job/(?P<pk>[\w]+)/?$", jc_views.delete_unplanned_job, name="delete_unplanned_job"),
    url(r"jobs/?$", jc_views.JobCardsList.as_view(), name="jobs"),
    url(r"^job_detail/(?P<pk>[\w]+)/?$", jc_views.JobActionView.as_view(), name="job_detail"),
    url(r"^planned_job_detail/(?P<pk>[\w]+)/?$", jc_views.PlannedJobActionView.as_view(), name="planned_job_detail"),
    url(r"^complete_job/([\w ]+)/?$", jc_views.complete_job, name="complete_job"),
    url(r"^get_resolvers/?$", jc_views.get_resolvers, name="get_resolvers"),
] + workorder_urls + preventative_task_urls         