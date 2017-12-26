
from __future__ import unicode_literals
import json
import os
import datetime

from django.test import TestCase
from django.test import Client
from django.shortcuts import reverse

from common_base.tests import TestDataMixin
from inv.models import Spares, Machine
from common_base.models import Account
from inventory_mmt import settings

class selectAjaxCalls(TestCase, TestDataMixin):
    """
    Tests for ajax form select widgets

    Testing the ajax calls for the json response that is used 
    to populate select form elements depending on the previous 
    input
    Tests:
        +update section
        +update subunit
        +update component
        +update subassembly

    """

    @classmethod
    def setUpClass(cls):
        super(selectAjaxCalls, cls).setUpClass()
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        super(selectAjaxCalls, cls).setUpTestData()
        cls.create_test_inventory_models()
        cls.create_dummy_accounts()

    def test_update_section(self):
        """Tests section update dictionary"""
        
        response = self.client.post(reverse("ajax:update_section"),
                         {"machine": "T_M"}, 
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertContains(response, "sections")
    
    def test_update_subunit(self):
        """Tests subunit update dictionary"""

        response = self.client.post(reverse("ajax:update_subunit"),
                         {"section": "T_SE"}, 
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        
        self.assertContains(response, "units")

    def test_update_subassembly(self):
        """Tests subassembly update dictionary"""

        response = self.client.post(reverse("ajax:update_subassembly"),
                         {"unit": "T_S"}, 
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
                
        self.assertContains(response, "subassemblies")

    def test_update_components(self):
        """Tests component update dictionary"""

        response = self.client.post(reverse("ajax:update_component"),
                         {"subassy": "T_SA"}, 
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertContains(response, "components")


class OtherAjaxTests(TestCase, TestDataMixin):
    """
    Tests ajax functions not associated with select widgets

    Tests:  
        test 
        test ajaxAuthenticate


    """
    
    @classmethod
    def setUpClass(cls):
        super(OtherAjaxTests, cls).setUpClass()
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        super(OtherAjaxTests, cls).setUpTestData()
        cls.create_test_inventory_models()
        cls.create_dummy_accounts()


    def test_get_users(self):
        """test is a json object is returned"""
        response = self.client.post(reverse("ajax:get-users"), 
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        dict = json.loads(response.content)
        self.assertTrue(len(dict["users"]) > 0)

    def test_get_combos_component(self):
        response = self.client.post(reverse("ajax:get-combos"),
                        {"str": "T_C",
                        "model": "component"},
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        dict = json.loads(response.content)
        self.assertTrue(len(dict["matches"]) == 1)

    def test_get_combos_inv(self):
        response = self.client.post(reverse("ajax:get-combos"),
                        {"str": "Test",
                        "model": "inv"},
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        dict = json.loads(response.content)
        self.assertTrue(len(dict["matches"]) == 2)


    def test_get_combos_machine(self):
        response = self.client.post(reverse("ajax:get-combos"),
                        {"str": "T_M",
                        "model": "machine"},
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        dict = json.loads(response.content)
        self.assertTrue(len(dict["matches"]) == 1)

    def test_get_combos_section(self):
        response = self.client.post(reverse("ajax:get-combos"),
                        {"str": "T_SE",
                        "model": "section"},
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        dict = json.loads(response.content)
        self.assertTrue(len(dict["matches"]) == 1)

    def test_get_combos_subassembly(self):
        response = self.client.post(reverse("ajax:get-combos"),
                        {"str": "T_SA",
                        "model": "subassembly"},
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        dict = json.loads(response.content)
        self.assertTrue(len(dict["matches"]) == 1)
    
    def test_get_combos_subunit(self):
        response = self.client.post(reverse("ajax:get-combos"),
                        {"str": "T_S",
                        "model": "subunit"},
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        dict = json.loads(response.content)
        self.assertTrue(len(dict["matches"]) == 1)

    def test_get_combos_spares(self):
        #find out why the test_data is not created
        Spares(name="test_spares",
                            description="some test description",
                            stock_id="T_S",
                            quantity=1).save()
        response = self.client.post(reverse("ajax:get-combos"),
                        {"str": "T_S",
                        "model": "spares"},
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        dict = json.loads(response.content)
        self.assertTrue(len(dict["matches"]) == 1)

    def test_add_run_data(self):
        """test made for machine run data"""
        response = self.client.post(reverse("ajax:add-run-data"),
                        {"start_date": datetime.date.today().strftime("%m/%d/%Y"),
                        "end_date": (datetime.date.today() + \
                        datetime.timedelta(days=7)).strftime("%m/%d/%Y"),
                        "machine": Machine.objects.first().pk,
                        "run_hours": "4",
                        "run_days": "3",
                        "monday": "",
                        "tuesday": "",
                        "wednesday": "",
                        "thursday": "",
                        "friday": "on",
                        "saturday": "on",
                        "sunday": "on"},
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertTrue(Machine.objects.first().run_data.all().count() == 1)


    def test_add_equipment(self):
        """used in the report generation form"""
        response = self.client.post(reverse("ajax:get-equipment"),
                        {"pk": Machine.objects.first().pk,
                        "type": "machine"},
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        dict = json.loads(response.content)
        self.assertTrue(dict[0]["pk"] is not None)
    
    def test_parse_csv_file(self):
        """especially considering the issue of the posted file name """
        #thread raises an exception, detailed testing of the parsers themselves 
        # will be done on common_base iteself
        settings.TEST_CONDITIONS = True

        with open(os.path.join("ajax", "test_files", "test_inv.csv"),
                                    "r") as fp:
            response = self.client.post(reverse("ajax:process-file"), {
                "csv_file": fp,
                "data_type": "machines"
            })

        self.assertTrue(response.status_code == 302)

    def test_stop_parsing(self):
        response = self.client.get(reverse("ajax:stop-parsing"))
        self.assertTrue(response.status_code == 302)

    def test_get_process_updates(self):
        """consider making the page aware of a process that is not running"""
        response = self.client.get(reverse("ajax:get-process-updates"))
        dict_ = json.loads(response.content)
        self.assertTrue(dict_["run_time"] is not None)

    def test_ajaxAuthenticate(self):
        """Test authentication via ajax"""

        response = self.client.post(reverse("ajax:ajax-authenticate"),
                                    {"username": "Test User",
                                    "password": "test123"},
                                    HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        
        self.assertTrue(json.loads(response.content)["authenticated"])