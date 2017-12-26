# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase, Client
from common_base.tests import TestDataMixin
from django.shortcuts import reverse
from checklists.models import Checklist

class ViewTests(TestCase, TestDataMixin):
    @classmethod
    def setUpClass(cls):
        super(ViewTests, cls).setUpClass()
        cls.client = Client

    @classmethod
    def setUpTestData(cls):
        super(ViewTests, cls).setUpTestData()
        cls.create_dummy_accounts()
        cls.create_test_checklist()
        cls.create_test_workorders()
        cls.create_test_preventative_task()

    def test_inbox(self):
        """tests the inbox page with no one logged in"""
        response = self.client.get(reverse("maintenance:inbox"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["message"], "")

    def test_inbox_with_user(self):
        """tests the inbox page with a user logged in and checks for the 
        appropriate message"""
        self.client.login(username="Test User", password="test123")
        response = self.client.get(reverse("maintenance:inbox"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["message"],"artisan:Hello Test User.")

    def test_get_machine_overview(self):
        """gets the machine overview page"""
        response = self.client.get(reverse("maintenance:machine-overview"))
        self.assertEqual(response.status_code, 200)

    def test_get_planned_maintenance_view(self):
        """gets the unfiltered maintenance view"""
        response = self.client.get(reverse("maintenance:planned-maintenance"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["object_list"]), 2)

    def test_get_planned_maintenance_view_filtered(self):
        """filtered one class of objects expect the object list to have one 
        element"""
        response = self.client.get(reverse("maintenance:planned-maintenance"),
            {"checklists":"on",
            "start_date": "",
            "end_date": ""})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["object_list"]), 1)