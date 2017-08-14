# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.test import Client
from django.shortcuts import reverse
from common_base.tests import TestDataMixin
import json

class selectAjaxCalls(TestCase, TestDataMixin):
    """Testing the ajax calls for the json response that is used 
    to populate select form elements depending on the previous 
    input"""

    @classmethod
    def setUpClass(cls):
        super(selectAjaxCalls, cls).setUpClass()
        cls.client = Client()


    @classmethod
    def setUpTestData(cls):
        super(selectAjaxCalls, cls).setUpTestData()
        cls.create_test_inventory_models()

    def test_update_subunit(self):
        response = self.client.post(reverse("ajax:update_subunit"),
                         {"machine": "T_M"}, 
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        
        self.assertContains(response, "units")


    def test_update_subassembly(self):
        response = self.client.post(reverse("ajax:update_subassembly"),
                         {"unit": "T_S"}, 
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        
        self.assertContains(response, "subassemblies")


    def test_update_components(self):
        response = self.client.post(reverse("ajax:update_components"),
                         {"subassy": "T_SA"}, 
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        
        self.assertContains(response, "components")