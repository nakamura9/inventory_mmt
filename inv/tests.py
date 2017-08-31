from django.test import TestCase
from django.test import Client
from django.shortcuts import reverse

from common_base.tests import TestDataMixin
from .models import *
import datetime

class ViewTests(TestCase, TestDataMixin):
    @classmethod
    def setUpTestData(cls):
        super(ViewTests, cls).setUpTestData()
        cls.create_test_inventory_models()

    @classmethod
    def setUpClass(cls):
        super(ViewTests, cls).setUpClass()
        cls.client = Client()

    #test detail pages
    def test_get_component_details(self):
        response = self.client.get(reverse("inventory:component_details", 
                                    kwargs={"pk": "T_C"}))
        
        self.assertEqual(response.status_code, 200)


    def test_get_section_details(self):
        response = self.client.get(reverse("inventory:section_details", 
                                    kwargs={"pk": "T_SE"}))
        
        self.assertEqual(response.status_code, 200)


    def test_get_machine_details(self):
        response = self.client.get(reverse("inventory:machine_details", 
                                    kwargs={"pk": "T_M"}))
        
        self.assertEqual(response.status_code, 200)


    def test_get_subunit_details(self):
        response = self.client.get(reverse("inventory:subunit_details", 
                                    kwargs={"pk": "T_S"}))
        
        self.assertEqual(response.status_code, 200)


    def test_get_subassembly_details(self):
        response = self.client.get(reverse("inventory:subassembly_details", 
                                    kwargs={"pk": "T_SA"}))
        
        self.assertEqual(response.status_code, 200)

    #test landing page
    def test_get_inventory_homepage(self):
        response = self.client.get(reverse("inventory:inventory-home"))
        
        self.assertEqual(response.status_code, 200)

    #get engineering inventory_forms
    def test_get_component_form(self):
        response = self.client.get(reverse("inventory:add_component"))
        
        self.assertEqual(response.status_code, 200)

    
    def test_get_machine_form(self):
        response = self.client.get(reverse("inventory:add_machine"))
        
        self.assertEqual(response.status_code, 200)

    def test_get_subunit_form(self):
        response = self.client.get(reverse("inventory:add_subunit"))
        
        self.assertEqual(response.status_code, 200)

    def test_get_subassembly_form(self):
        response = self.client.get(reverse("inventory:add_subassembly"))
        
        self.assertEqual(response.status_code, 200)

    
    def test_get_section_form(self):
        response = self.client.get(reverse("inventory:add_section"))
        
        self.assertEqual(response.status_code, 200)

    #test get inventory forms
    def test_get_raw_materials(self):
        response = self.client.get(reverse("inventory:raw-materials"))
        
        self.assertEqual(response.status_code, 200)

    def test_get_category(self):
        response = self.client.get(reverse("inventory:new-category"))
        
        self.assertEqual(response.status_code, 200)
    
    
    def test_get_order_details(self):
        response = self.client.get(reverse("inventory:order-details",
                                            kwargs={"pk":"100"}))
        
        self.assertEqual(response.status_code, 200)


    def test_get_order_form(self):
        response = self.client.get(reverse("inventory:new-order"))
        
        self.assertEqual(response.status_code, 200)


    def test_get_inventory_details(self):
        response = self.client.get(reverse("inventory:order-details",
                                            kwargs={"pk":"100"}))
        
        self.assertEqual(response.status_code, 200)


    def test_get_inventory_form(self):
        response = self.client.get(reverse("inventory:new-inventory-item"))
        
        self.assertEqual(response.status_code, 200)


    #test posting and deleting of engineering inventory
    def test_post_check_and_delete_component_form(self):
        self.client.post(reverse("inventory:add_component"),
                                    data={"unique_id":"P_T_C",
                                            "component_name": "Posted Test Component",
                                            "machine": "T_M",
                                            "section": "T_SE",
                                            "subunit": "T_S",
                                            "subassembly":"T_SA"})
        
        self.assertIsInstance(Component.objects.get(pk="P_T_C"), Component)
        
        response = self.client.get(reverse("inventory:delete_component", 
                                            args=["P_T_C"]))

        self.assertEqual(response.status_code, 302)#redirects


    def test_post_check_and_delete_component_form(self):
        self.client.post(reverse("inventory:add_section"),
                                    data={"unique_id":"P_T_SE",
                                            "section_name": "Posted Test Component",
                                            "machine": "T_M",})
        
        self.assertIsInstance(Section.objects.get(pk="P_T_SE"), Section)
        
        response = self.client.get(reverse("inventory:delete_section", 
                                            args=["P_T_SE"]))

        self.assertEqual(response.status_code, 302)#redirects


    def test_post_check_and_delete_machine_form(self):
        response = self.client.post(reverse("inventory:add_machine"),
                                    data={"unique_id":"P_T_M",
                                            "machine_name": "Posted Test Machine",
                                            "manufacturer": "Test Manufacturer",
                                            "commissioning_date":datetime.date.today()})
        
        self.assertIsInstance(Machine.objects.get(pk="P_T_M"), Machine)

        response = self.client.get(reverse("inventory:delete_machine", 
                                            args=["P_T_M"]))
                                            
        self.assertEqual(response.status_code, 302)#redirects


    def test_post_check_and_delete_subunit_form(self):
        response = self.client.post(reverse("inventory:add_subunit"),
                                    data={"unique_id":"P_T_S",
                                            "unit_name": "Posted Test SubUnit",
                                            "section": "T_SE",
                                            "machine": "T_M"})
        
        self.assertIsInstance(SubUnit.objects.get(pk="P_T_S"), SubUnit)

        response = self.client.get(reverse("inventory:delete_subunit", 
                                            args=["P_T_S"]))
                                            
        self.assertEqual(response.status_code, 302)#redirects

    def test_post_check_and_delete_subassembly_form(self):
        response = self.client.post(reverse("inventory:add_subassembly"),
                                    data={"unique_id":"P_T_SA",
                                            "unit_name": "Posted Test SubAssembly",
                                            "machine": "T_M",
                                            "section": "T_SE",
                                            "subunit": "T_S"})
        
        self.assertIsInstance(SubAssembly.objects.get(pk="P_T_SA"), SubAssembly)

        response = self.client.get(reverse("inventory:delete_subassembly", 
                                            args=["P_T_SA"]))
                                            
        self.assertEqual(response.status_code, 302)#redirects

    #test posting of inventory forms
    def test_post_check_and_delete_order_form(self):
        response = self.client.post(reverse("inventory:new-order"),
                                    data={"order_number":"101",
                        "description":"Test Description",
                        "quantity":"100",
                        "unit_price":"0.1",
                        "manufacture_date":datetime.date.today(),
                        "flute_profile":"a",
                        "liner":"kraft",
                        "layers":"1",
                        "delivery_date":datetime.date.today() + \
                            datetime.timedelta(days=5),
                        "customer":"Test Customer",
                        "production_status":"planned",
                        "delivery_status":"storage"})
        
        self.assertIsInstance(Order.objects.get(pk="101"), Order)

        response = self.client.get(reverse("inventory:order-delete", 
                                            kwargs={"pk":"101"}))
                                            
        self.assertEqual(response.status_code, 302)#redirects


    def test_post_check_and_delete_inventory_form(self):
        #delete view for inventory not yet implemented
        #  
        response = self.client.post(reverse("inventory:new-inventory-item"),
                                    data={"serial_number":"101",
                                        "name":"Test Inventory Item",
                                        "order_number":"1",
                                        "quantity":"100",
                                        "unit":"ea",
                                        "order_date":datetime.date.today(),
                                        "category": "1",
                                        "supplier":"Test Supplier",
                                        "unit_price":"0.1",
                                        "min_stock_level":"20",
                                        "reorder_quantity":"200"})
        
        self.assertIsInstance(InventoryItem.objects.get(pk="101"), InventoryItem)


class ModelTests(TestCase):
    def test_create_plant(self):
        pass

    def test_create_machine(self):
        pass

    def test_machine_checklist_coverage(self):
        pass

    def test_n_breakdowns(self):
        pass

    def test_create_subunit(self):
        pass

    def test_create_subassembly(self):
        pass

    def test_create_component(self):
        pass

    def test_create_order(self):
        pass

    def test_create_category(self):
        pass

    def test_create_raw_material(self):
        pass

    def test_create_inventory_item(self):
        pass