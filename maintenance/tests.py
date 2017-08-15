# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from common_base.tests import TestDataMixin
class ViewTests(TestCase, TestDataMixin):
    @classmethod
    def setUpClass(cls):
        super(ViewTests, cls).setUpClass()
        #do something here

    @classmethod
    def setUpTestData(cls):
        super(ViewTests, cls).setUpTestData()
        cls.create_test_checklist()

    def test_inbox(self):
        response = self.client.get(reverse("maintenance:inbox"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["message"], "No user logged in")
