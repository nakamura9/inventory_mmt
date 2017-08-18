from django.conf.urls import url
from machine_learning.views import *
appname = "machine-learning"

urlpatterns = [
    url(r'^home/?$', Home.as_view(), name="home"),
    url(r'^regression/?$', RegressionView.as_view(), name="regression"),
    url(r'^classification/?$', ClassificationView.as_view(), name="classification"),
    url(r'^clustering/?$', ClusterView.as_view(), name="clustering"),
]