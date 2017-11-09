from django.conf.urls import url
import views
spares_urls = [
    url(r'^spares-details/(?P<pk>[\d]+)/?$', views.SparesDetail.as_view(), name="spares-details"),
    url(r'^spares-create/?$', views.SparesCreate.as_view(), name="spares-create"),
    url(r'^spares-update/(?P<pk>[\d]+)/?$', views.SparesUpdate.as_view(), name="spares-update"),
    ]


asset_urls = [
    url(r'^asset-details/(?P<pk>[\d]+)/?$', views.AssetDetail.as_view(), name="asset-details"),
    url(r'^asset-create/?$', views.AssetCreate.as_view(), name="asset-create"),
    url(r'^asset-update/(?P<pk>[\d]+)/?$', views.AssetUpdate.as_view(), name="asset-update"),
    ]


component_urls =[ 
    
    url(r'^component_details/(?P<pk>[ -~]+)/?$', views.ComponentView.as_view(),
             name="component_details"),
    url(r'^add_component/?$', views.ComponentCreateView.as_view(), name="add_component"),
    url(r'edit_component/(?P<pk>[ -~]+)/?$', views.ComponentEditView.as_view(), 
            name="edit_component"),
    url(r'delete_component/([ -~]+)/?$', views.delete_component, 
            name="delete_component"),
    
    ]

machine_urls = [

    url(r'^machine_details/(?P<pk>[ -~]+)/?$', views.MachineView.as_view(), 
            name="machine_details"),
    url(r'^add_machine/?$', views.MachineCreateView.as_view(), name="add_machine"),
    url(r'^edit_machine/(?P<pk>[ -~]+)/?$', views.MachineEditView.as_view(),
             name="edit_machine"),
    url(r'^delete_machine/([ -~]+)/?$', views.delete_machine,
             name="delete_machine"),

]

subunit_urls = [
    
    url(r'edit_subunit/(?P<pk>[ -~]+)/?$', views.SubunitEditView.as_view(), 
            name="edit_subunit"),
    url(r'^add_subunit/?$', views.SubUnitCreateView.as_view(), name="add_subunit"),
    url(r'^subunit_details/(?P<pk>[ -~]+)/?$', views.SubUnitView.as_view(), 
            name="subunit_details"),
    url(r'delete_subunit/([ -~]+)/?$', views.delete_subunit, name="delete_subunit"),
    
]

subassembly_urls = [

    url(r'^subassembly_details/(?P<pk>[ -~]+)/?$', views.SubAssyView.as_view(), 
            name="subassembly_details"),
    url(r'^add_subassembly/?$', views.SubAssyCreateView.as_view(), name="add_subassembly"),
    url(r'^edit_subassembly/(?P<pk>[ -~]+)/?$', views.SubAssyEditView.as_view(), 
            name="edit_subassembly"),
    url(r'^delete_subassembly/([ -~]+)/?$', views.delete_subassembly, 
            name="delete_subassembly"),

]

section_urls = [
    url(r'^add_section/$', views.SectionCreateView.as_view(), name="add_section"),
    url(r'^edit_section/(?P<pk>[ -~]+)/$', views.SectionUpdateView.as_view(), 
    name="edit_section"),
    url(r'^section_details/(?P<pk>[ -~]+)/$', views.SectionDetailView.as_view(), 
    name="section_details"),
    url(r'^delete_section/([ -~]+)/$', views.delete_section, 
    name="delete_section"),
]

order_urls = [

    url(r'^order-details/(?P<pk>[ -~]+)/?$', views.OrderDetailView.as_view(), 
        name='order-details'),
    url(r'^order-update/(?P<pk>[ -~]+)/?$', views.OrderUpdateView.as_view(),
        name='order-update'),
    url(r'^order-list/?$', views.OrderList.as_view(), name='order-list'),
    url(r'^order-delete/(?P<pk>[ -~]+)/?$', views.delete_order, 
        name='order-delete'),
    url(r'^new-order/?$', views.OrderCreateView.as_view(), name='new-order'),
    
]

production_inventory_urls = [
    
    url(r'^new-inventory-item/?$', views.InventoryItemFormView.as_view(), 
            name='new-inventory-item'),
    url(r'^inventory-list/(?P<filter>[ -~]+)/?$', views.InventoryListView.as_view(),
             name='inventory-list'),
    url(r'^inventory-details/(?P<pk>[ -~]+)/?$', 
        views.InventoryItemDetailView.as_view(), name='inventory-details'),

]

urlpatterns = [
    
    url(r'^inventory-home/?$', views.invHome.as_view(), name="inventory-home"),   
    url(r'^add_plant/?$', views.PlantCreateView.as_view(), name="add_plant"),
    url(r'^engineering-inventory/?$', views.EngineeringInventoryView.as_view(), 
            name='engineering-inventory'),
    url(r'^raw-materials/?$', views.CategoryList.as_view(), name='raw-materials'),
    url(r'^new-category/?$', views.CategoryCreateView.as_view(), name='new-category'),

] + component_urls + machine_urls + subassembly_urls + subunit_urls + \
    order_urls + production_inventory_urls + section_urls + asset_urls + \
    spares_urls