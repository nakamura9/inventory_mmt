from django.test import TestCase, Client
from common_base.tests import TestDataMixin
from django.shortcuts import reverse
from .models import WorkOrder, PreventativeTask
import datetime
from common_base.models import Account
from inv.models import Machine, Section, SubUnit, SubAssembly, Component
from django.utils import timezone


class ViewTests(TestCase, TestDataMixin):
    @classmethod
    def setUpClass(cls):
        super(ViewTests, cls).setUpClass()
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        super(ViewTests, cls).setUpTestData()
        cls.create_dummy_accounts()
        cls.create_test_inventory_models()


    def setUp(self):
        self.common_data = {"description": "Test Description",
                    "creation_epoch": datetime.date.today(),
                    "resolver": Account.objects.first(),
                    "estimated_time": "0030",
                    "completed": False,
                    "machine": Machine.objects.first(),
                    "section": Section.objects.first(),
                    "subunit": SubUnit.objects.first()
                    }
    
    

