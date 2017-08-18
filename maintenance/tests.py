# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase, Client
from common_base.tests import TestDataMixin
from django.shortcuts import reverse

class ViewTests(TestCase, TestDataMixin):
    @classmethod
    def setUpClass(cls):
        super(ViewTests, cls).setUpClass()
        cls.client = Client

    @classmethod
    def setUpTestData(cls):
        super(ViewTests, cls).setUpTestData()
        #cls.create_test_checklist()

    def test_inbox(self):
        response = self.client.get(reverse("maintenance:inbox"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["message"], "No user logged in")
