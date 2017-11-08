
from __future__ import unicode_literals
import json

from django.test import TestCase
from django.test import Client
from django.shortcuts import reverse

from common_base.tests import TestDataMixin
from common_base.models import Account


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
        test add task
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


    def test_add_task(self):
        """"Tests task addition response, '0' indicates success"""

        session = self.client.session
        session["tasks"] = []
        session.save()
        response = self.client.post(reverse("ajax:add_task"), 
                                    {"task":"Some Test Task"},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.content, "0")

    def test_ajaxAuthenticate(self):
        """Test authentication via ajax"""

        response = self.client.post(reverse("ajax:ajax-authenticate"),
                                    {"username": "Test User",
                                    "password": "test123"},
                                    HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        
        self.assertEqual(json.loads(response.content)["authenticated"], False)