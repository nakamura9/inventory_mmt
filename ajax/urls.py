from django.conf.urls import url
from .views import *
urlpatterns = [
    url(r"^update_subunit/?$", update_subunit, name="update_subunit"),# not to be confused with editing
    url(r"^update_subassembly/?$", update_subassembly, name="update_subassembly"),
    url(r"^update_components/?$", update_components, name="update_components"),

]