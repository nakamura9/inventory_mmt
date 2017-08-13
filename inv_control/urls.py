from django.conf.urls import url
import views as ic_views 

app_name="control_forms"

urlpatterns = [
    url(r'^add_machine/?$', ic_views.machineView.as_view(), name="add_machine"),
    url(r'add_subunit/?$', ic_views.subunitView.as_view(), name="add_subunit"),
    url(r'add_subassembly/?$', ic_views.subassyView.as_view(), name="add_subassembly"),
    url(r'add_component/?$', ic_views.componentView.as_view(), name="add_component"),
    url(r'add_plant/?$', ic_views.plantView.as_view(), name="add_plant"),
    url(r'^edit_machine/(?P<pk>[ -~]+)/?$', ic_views.machineEditView.as_view(), name="edit_machine"),
    url(r'edit_subunit/(?P<pk>[ -~]+)/?$', ic_views.subunitEditView.as_view(), name="edit_subunit"),
    url(r'edit_subassembly/(?P<pk>[ -~]+)/?$', ic_views.subassyEditView.as_view(), name="edit_subassembly"),
    url(r'edit_component/(?P<pk>[ -~]+)/?$', ic_views.componentEditView.as_view(), name="edit_component"),
    url(r'delete_subunit/([ -~]+)/?$', ic_views.delete_subunit, name="delete_subunit"),
    url(r'delete_subassembly/([ -~]+)/?$', ic_views.delete_subassembly, name="delete_subassembly"),
    url(r'delete_component/([ -~]+)/?$', ic_views.delete_component, name="delete_component"),
    url(r'^delete_machine/([ -~]+)/?$', ic_views.delete_machine, name="delete_machine"),
    url(r'^browse/?$', ic_views.browseView.as_view(), name='browse'),
    url(r'^raw-materials/?$', ic_views.CategoryList.as_view(), name='raw-materials'),
    url(r'^finished-products/?$', ic_views.OrderCreateView.as_view(), name='finished-products'),
    url(r'^finished-products-details/(?P<pk>[ -~]+)/?$', ic_views.OrderDetailView.as_view(), name='finished-products-details'),
    url(r'^finished-products-update/(?P<pk>[ -~]+)/?$', ic_views.OrderUpdateView.as_view(), name='finished-products-update'),
    url(r'^finished-products-list/?$', ic_views.OrderList.as_view(), name='finished-products-list'),
    url(r'^finished-products-delete/(?P<pk>[ -~]+)/?$', ic_views.delete_order, name='finished-products-delete'),
    url(r'^new-category/?$', ic_views.categoryForm.as_view(), name='new-category'),
    url(r'^new-inventory-item/?$', ic_views.inventoryItemFormView.as_view(), name='new-inventory-item'),
    url(r'^inventory-list/(?P<filter>[ -~]+)/?$', ic_views.inventoryListView.as_view(), name='inventory-list'),
    url(r'^inventory-details/(?P<pk>[ -~]+)/?$', ic_views.inventoryItemDetailView.as_view(), name='inventory-details'),
    url(r'^$', ic_views.show, name="show"),
]