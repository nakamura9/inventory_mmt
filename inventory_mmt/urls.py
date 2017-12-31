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

from django.conf.urls import url, include, static

from django.conf import settings
from django.contrib import admin
from common_base.views import *
from inv import urls as inv_urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^feature-tests/$', test_features),
    url(r'^inventory/', include(inv_urls, namespace="inventory")),
    url(r'^logout/$', logout, name="logout"),
    url(r'^login/$', login, name="login"),
    url(r'^about/$', AboutTemplateView.as_view(), name="about"),
    url(r'^sign_up/?$', sign_up, name="sign_up"),
    url(r'^jobcards/', include("jobcards.urls")),
    url(r'^checklists/', include("checklists.urls")),
    url(r'^machine-learning/', include("machine_learning.urls", namespace="machine-learning")),
    url(r'^planning/', include("planning.urls", namespace="planning")),
    url(r'^ajax/', include("ajax.urls", namespace = "ajax")),
    url(r'reports/', include("reports.urls",  namespace="reports")),
    url(r'^maintenance/', include("maintenance.urls", namespace="maintenance")),
] + static.static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)
