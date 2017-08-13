"""inventory_mmt URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from inv import views as inv_views
from inv.views import sign_up, logout, login
from inv import urls as inv_urls
from inv.views import *


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^client/', include(inv_urls, namespace="client")),
    url(r'^logout/$', logout, name="logout"),
    url(r'^login/$', login, name="login"),
    url(r'^sign_up/?$', sign_up, name="sign_up"),
    url(r'^jobcards/', include("jobcards.urls")),
    url(r'^checklists/', include("checklists.urls")),
    url(r'^maintenance-calendar/', include("maintenance_calendar.urls", namespace="maintenance-calendar")),
    url(r'^machine-learning/', include("machine_learning.urls", namespace="machine-learning")),
    url(r'^rca/', include("rca.urls", namespace="rca")),
    url(r'^production-calendar/', include("production_calendar.urls", namespace="production-calendar")),
    url(r'^inventory_control/', include("inv_control.urls", namespace = "control_forms"))
]
