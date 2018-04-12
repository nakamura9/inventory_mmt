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

    def test_get_component_details_linked(self):
        comp = Component.objects.get(pk="T_C")
        comp.spares_data.add(Spares.objects.first())
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

    def test_post_check_and_delete_component_w_spares_form(self):
        sp = Spares.objects.first()
        self.client.post(reverse("inventory:add_component"),
            data={
                "unique_id":"P_T_C_W_S",
                "component_name": "Posted Test Component With Spares",
                "machine": "T_M",
                "section": "T_SE",
                "subunit": "T_S",
                "spares_data": sp.stock_id,
                "subassembly":"T_SA"})
        cmp= Component.objects.get(pk="P_T_C_W_S")
        self.assertIsInstance(cmp, Component)
        self.assertNotEqual(cmp.spares_data, None) 
        response = self.client.get(reverse(
            "inventory:delete_component", args=["P_T_C_W_S"]))
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

    def test_edit_machine(self):
        response=self.client.get(reverse("inventory:edit_machine",
            kwargs={"pk": Machine.objects.first().pk}))
        self.assertEqual(response.status_code, 200)

    def test_edit_section(self):
        response=self.client.get(reverse("inventory:edit_section",
            kwargs={"pk": Section.objects.first().pk}))
        self.assertEqual(response.status_code, 200)
    
    def test_edit_subunit(self):
        response=self.client.get(reverse("inventory:edit_subunit",
            kwargs={"pk": SubUnit.objects.first().pk}))
        self.assertEqual(response.status_code, 200)

    def test_edit_subassembly(self):
        response=self.client.get(reverse("inventory:edit_subassembly",
            kwargs={"pk": SubAssembly.objects.first().pk}))
        self.assertEqual(response.status_code, 200)
    
    def test_edit_component(self):
        response=self.client.get(reverse("inventory:edit_component",
            kwargs={"pk": Component.objects.first().pk}))
        self.assertEqual(response.status_code, 200)

    def test_edit_component_post(self):
        response=self.client.post(reverse("inventory:edit_component",
            kwargs={"pk": Component.objects.first().pk}),
            data={
                "unique_id":"T_C",
                "component_name": "Posted Test Component",
                "machine": "T_M",
                "section": "T_SE",
                "subunit": "T_S",
                "subassembly":"T_SA"})
        self.assertEqual(response.status_code, 302)

    #test posting of inventory forms
    


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

    def test_machine_availability_on_date(self):
        self.create_dummy_accounts()
        self.create_test_workorders()#one hour downtime

        mech = Machine.objects.get(unique_id="T_M")
        mech.run_data.add(RunData.objects.first())
        availability = mech.availability_on_date(self.today)
        self.assertEqual(round(availability, 2), 0.0)

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
        if self.today.weekday() < 3:
            self.assertTrue(mech.is_running_on_date(self.today))

    def test_spares_search(self):
        response=self.client.get(reverse('inventory:spares-list'), {"search": "01"})
        self.assertEqual(response.status_code, 200)

    def test_delete_run_data(self):
        RunData(start_date = self.today,
            end_date = self.today + datetime.timedelta(days=7),
            run_hours = 1,
            thursday=True,
            friday=True,
            saturday=True).save()
        response =self.client.get(reverse("inventory:delete-run-data",
            kwargs={"pk":RunData.objects.latest("pk").pk,
                "mech_pk": Machine.objects.first()}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(RunData.objects.all().count(), 1)

    def test_run_days(self):
        
        RunData(start_date = self.today,
            end_date = self.today + datetime.timedelta(days=7),
            run_hours = 1,
            thursday=True,
            friday=True,
            saturday=True).save()

        self.assertEqual(RunData.objects.latest("pk").run_days, 3)