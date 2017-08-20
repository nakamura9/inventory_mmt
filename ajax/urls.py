from django.conf.urls import url
from .views import *
urlpatterns = [
    url(r"^update_section/?$", update_section, name="update_section"),
    url(r"^update_subunit/?$", update_subunit, name="update_subunit"),
    url(r"^update_subassembly/?$", update_subassembly, name="update_subassembly"),
    url(r"^update_component/?$", update_components, name="update_component"),
    url(r'^ajax-authenticate/?$', ajaxAuthenticate, name="ajax-authenticate"),

]