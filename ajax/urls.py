from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r"^update_section/?$", update_section, name="update_section"),
    url(r"^update_subunit/?$", update_subunit, name="update_subunit"),
    url(r"^update_subassembly/?$", update_subassembly, name="update_subassembly"),
    url(r"^update_component/?$", update_components, name="update_component"),
    url(r'^ajax-authenticate/?$', ajaxAuthenticate, name="ajax-authenticate"),
    url(r'^get-users$', get_users, name="get-users"),
    url(r'^add-category/?$', add_category,name="add-category"),
    url(r'^get-combos/?$', get_combos, name="get-combos"),
    url(r'^process-file$', parse_csv_file, name="process-file"),
    url(r'^test-process-file$', test_parse_csv_file, name="test-process-file"),
    url(r'^get-process-updates$', get_run_data, name="get-process-updates"),
]