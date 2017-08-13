from django.conf.urls import url
from rca.views import *

urlpatterns = [
    url(r'^rca-form/?$', RCAForm.as_view(), name="rca-form"),
    url(r'^ishikawa/?$', Ishikawa.as_view(), name="ishikawa"),
]