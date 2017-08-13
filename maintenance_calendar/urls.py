from django.conf.urls import url
import views
urlpatterns = [
    url(r'^month/(?P<year>[\d]+)/(?P<month>[\d]+)/?$', views.MonthView.as_view(), name="month"),
    url(r'^day/(?P<year>[\d]+)/(?P<month>[\d]+)/(?P<day>[\d]+)?$', views.DayView.as_view(), name="day"),
    url(r'^week/(?P<year>[\d]+)/(?P<month>[\d]+)/(?P<week>[\d]+)?$', views.WeekView.as_view(), name="week")
]
