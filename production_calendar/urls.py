from django.conf.urls import url
from production_calendar.views import *
urlpatterns = [
    url(r'^month/([0-9]{4})/([0-9]+)/?$', MonthView.as_view(), name="month"),
    url(r'^week/([0-9]{4})/([0-9]+)/([1-6]{1})/?$', WeekView.as_view(), name="week"),
    url(r'^day//([0-9]{4})/([0-9]+)/([0-9]+)/?$', DayView.as_view(), name="day")
]