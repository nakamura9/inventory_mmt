from django.conf.urls import url

import views


production_urls = [
    url(r'^production/month/(?P<year>[\d]+)/(?P<month>[\d]+)/?$', 
    views.productionMonthView.as_view(), name="production-month"),
    url(r'^production/day/(?P<year>[\d]+)/(?P<month>[\d]+)/(?P<day>[\d]+)/?$', 
    views.productionDayView.as_view(), name="production-day"),
    url(r'^production/week/(?P<year>[\d]+)/(?P<month>[\d]+)/(?P<week>[\d]+)/?$', 
    views.productionWeekView.as_view(), name="production-week"),
]



maintenance_urls = [
    url(r'^maintenance/month/(?P<year>[\d]+)/(?P<month>[\d]+)/?$', 
    views.maintenanceMonthView.as_view(), name="maintenance-month"),
    url(r'^maintenance/month/?$', 
    views.maintenanceMonthView.as_view(), name="maintenance-month"),
    url(r'^maintenance/day/(?P<year>[\d]+)/(?P<month>[\d]+)/(?P<day>[\d]+)/?$', 
    views.maintenanceDayView.as_view(), name="maintenance-day"),
    url(r'^maintenance/week/(?P<year>[\d]+)/(?P<month>[\d]+)/(?P<week>[\d]+)/?$', 
    views.maintenanceWeekView.as_view(), name="maintenance-week"),
]


urlpatterns = [] + maintenance_urls + production_urls
