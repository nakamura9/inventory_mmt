import datetime

from django.shortcuts import reverse
from django.test import TestCase, Client

from common_base.models import Account
from inventory_mmt import settings
from common_base.tests import TestDataMixin
from .models import *

class ViewTests(TestCase, TestDataMixin):
    """Tests for views for creation, viewing, updating and deleting inventory models

    GET tests take a url, use the client to retrieve and test if the status_code is 200.
    POST tests create a database entry via a url, test if the entry is present in the test database, use another url to delete the entry and test if the request resulted in a redirect(302) which indicates success."""
    
    @classmethod
    def setUpTestData(cls):
        super(ViewTests, cls).setUpTestData()
        cls.create_test_inventory_models()

    @classmethod
    def setUpClass(cls):
        super(ViewTests, cls).setUpClass()
        cls.client = Client()
        settings.TEST_CONDITIONS = True

    #test detail pages
    def test_get_component_details(self):
        response = self.client.get(
            reverse("inventory:component_details", 
            kwargs={"pk": "T_C"}))
        
        self.assertEqual(response.status_code, 200)


    def test_get_section_details(self):
        response = self.client.get(reverse(
            "inventory:section_details", 
            kwargs={"pk": "T_SE"}))
        self.assertEqual(response.status_code, 200)


    def test_get_machine_details(self):
        response = self.client.get(reverse(
            "inventory:machine_details", 
            kwargs={"pk": "T_M"}))
        self.assertEqual(response.status_code, 200)


    def test_get_subunit_details(self):
        response = self.client.get(reverse(
            "inventory:subunit_details", 
            kwargs={"pk": "T_S"}))
        self.assertEqual(response.status_code, 200)


    def test_get_subassembly_details(self):
        response = self.client.get(reverse(
            "inventory:subassembly_details", 
            kwargs={"pk": "T_SA"}))
        self.assertEqual(response.status_code, 200)

    #test landing page
    def test_get_inventory_homepage(self):
        response = self.client.get(reverse("inventory:inventory-home"))        
        self.assertEqual(response.status_code, 200)

    def test_get_engineering_page(self):
        response = self.client.get(reverse(
            "inventory:engineering-inventory"))
        self.assertEqual(response.status_code, 200)

    def test_get_spares_list_page(self):
        response = self.client.get(reverse(
            "inventory:spares-list"))
        self.assertEqual(response.status_code, 200)

    #get engineering inventory_forms
    def test_get_component_form(self):
        response = self.client.get(reverse(
            "inventory:add_component"))
        self.assertEqual(response.status_code, 200)

    def test_get_machine_form(self):
        response = self.client.get(reverse(
            "inventory:add_machine"))        
        self.assertEqual(response.status_code, 200)

    def test_get_subunit_form(self):
        response = self.client.get(reverse(
            "inventory:add_subunit"))
        self.assertEqual(response.status_code, 200)

    def test_get_subassembly_form(self):
        response = self.client.get(reverse(
            "inventory:add_subassembly"))
        self.assertEqual(response.status_code, 200)
   
    def test_get_section_form(self):
        response = self.client.get(reverse(
            "inventory:add_section"))
        self.assertEqual(response.status_code, 200)

    #test posting and deleting of engineering inventory
    def test_post_check_and_delete_component_form(self):
        self.client.post(reverse("inventory:add_component"),
            data={
                "unique_id":"P_T_C",
                "component_name": "Posted Test Component",
                "machine": "T_M",
                "section": "T_SE",
                "subunit": "T_S",
                "subassembly":"T_SA"})
        
        self.assertIsInstance(Component.objects.get(pk="P_T_C"), Component) 
        response = self.client.get(reverse(
            "inventory:delete_component", args=["P_T_C"]))
        self.assertEqual(response.status_code, 302)#redirects

    def test_post_check_and_delete_section_form(self):
        self.client.post(reverse("inventory:add_section"),
            data={
                "unique_id":"P_T_SE",
                "section_name": "Posted Test Section",
                "machine": "T_M"})
        self.assertIsInstance(Section.objects.get(pk="P_T_SE"), Section)
        response = self.client.get(reverse(
            "inventory:delete_section",args=["P_T_SE"]))
        self.assertEqual(response.status_code, 302)#redirects

    def test_post_check_and_delete_machine_form(self):
        response = self.client.post(reverse("inventory:add_machine"),
            data={
                "unique_id":"P_T_M",
                "machine_name": "Posted Test Machine",
                "manufacturer": "Test Manufacturer",
                "commissioning_date":datetime.date.today()})
        self.assertIsInstance(Machine.objects.get(pk="P_T_M"), Machine)
        response = self.client.get(reverse(
            "inventory:delete_machine", args=["P_T_M"]))
        self.assertEqual(response.status_code, 302)#redirects


    def test_post_check_and_delete_subunit_form(self):
        response = self.client.post(reverse("inventory:add_subunit"),
            data={
                "unique_id":"P_T_S",
                "unit_name": "Posted Test SubUnit",
                "section": "T_SE",
                "machine": "T_M"})        
        self.assertIsInstance(SubUnit.objects.get(pk="P_T_S"), SubUnit)
        response = self.client.get(reverse(
            "inventory:delete_subunit", args=["P_T_S"]))
        self.assertEqual(response.status_code, 302)#redirects

    def test_post_check_and_delete_subassembly_form(self):
        response = self.client.post(reverse("inventory:add_subassembly"),
            data={
                "unique_id":"P_T_SA",
                "unit_name": "Posted Test SubAssembly",
                "machine": "T_M",
                "section": "T_SE",
                "subunit": "T_S"})
        self.assertIsInstance(SubAssembly.objects.get(pk="P_T_SA"), SubAssembly)
        response = self.client.get(reverse(
            "inventory:delete_subassembly", args=["P_T_SA"]))
        self.assertEqual(response.status_code, 302)#redirects

    #test posting of inventory forms
    """def test_post_check_and_delete_order_form(self):
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
        
        self.assertIsInstance(InventoryItem.objects.get(pk="101"), InventoryItem)"""


class TestModelMethods(TestCase, TestDataMixin):
    @classmethod
    def setUpTestData(cls):
        super(TestModelMethods, cls).setUpTestData()
        cls.create_test_inventory_models()

    @classmethod
    def setUpClass(cls):
        super(TestModelMethods, cls).setUpClass()
        cls.today = datetime.date.today()

    def test_run_data_is_running(self):
        run_data = RunData.objects.first()
        if self.today.weekday() < 3:
            self.assertTrue(run_data.is_running(self.today))
        else:
            self.assertFalse(run_data.is_running(self.today))

    def test_run_data_total_run_hours(self):
        """create a second run data object that limits the total run time of the system"""
        run_data = RunData.objects.first()#3 days * 1 hour each
        self.assertEqual(run_data.total_run_hours, 3)

    def test_machine_availability_over_period(self):
        self.create_dummy_accounts()
        self.create_test_workorders()#one hour downtime

        mech = Machine.objects.get(unique_id="T_M")
        mech.run_data.add(RunData.objects.first()) # 3 hours
        availability = mech.availability_over_period(self.today,
            self.today + datetime.timedelta(days=7)) # 66%
        self.assertEqual(round(availability, 2), 66.67)

    def test_machine_planned_downtime_over_period(self):
        self.create_test_preventative_task()
        mech = Machine.objects.get(pk="T_M")
        dt = mech.planned_downtime_over_period(self.today,
            self.today + datetime.timedelta(days=7))
        self.assertEqual(dt, 1.0)
        
    def test_machine_unplanned_downtime_over_period(self):
        self.create_dummy_accounts()
        self.create_test_workorders()#one hour downtime

        mech = Machine.objects.get(unique_id="T_M")
        dt = mech.unplanned_downtime_over_period(self.today,
            self.today + datetime.timedelta(days=7))
        self.assertEqual(dt, 1)

    def test_machine_run_hours_over_period(self):
        mech = Machine.objects.get(unique_id="T_M")
        hrs = mech.run_hours_over_period(self.today,
            self.today + datetime.timedelta(days=7))
        self.assertEqual(hrs, 0)
        mech.run_data.add(RunData.objects.first())
        hrs = mech.run_hours_over_period(self.today,
            self.today + datetime.timedelta(days=7))
        self.assertEqual(hrs, 3)
        RunData(
            start_date = datetime.date.today(),
            end_date = datetime.date.today() + datetime.timedelta(days=7),
            run_days = 2,
            run_hours = 6,
            thursday=True,
            friday=True).save()
        mech.run_data.add(RunData.objects.latest("pk"))
        hrs = mech.run_hours_over_period(self.today,
            self.today + datetime.timedelta(days=7))
        self.assertEqual(hrs, 15)

    def test_machine_run_on_date(self):
        mech = Machine.objects.get(pk="T_M")
        self.assertEqual(mech.run_on_date(self.today).count(), 0)
        mech.run_data.add(RunData.objects.first())
        self.assertEqual(mech.run_on_date(self.today).count(), 1)

    def test_machine_is_running_on_date(self):
        mech = Machine.objects.get(pk="T_M")
        self.assertFalse(mech.is_running_on_date(self.today))
        mech.run_data.add(RunData.objects.first())
        self.assertTrue(mech.is_running_on_date(self.today))