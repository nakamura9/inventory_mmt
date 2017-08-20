# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from inv import models as inv_models
from checklists import models as ch_models
from jobcards import models as jb_models
from .models import Account
import datetime
from django.utils import timezone
import random

class TestAccount(TestCase):
    def test_create_account(self):
        Account(username= "Test User",
                first_name="Test",
                last_name="User",
                password="test123",
                role="artisan").save()

        self.assertIsInstance(Account.objects.get(username="Test User"),
                                Account)


class TestDataMixin(object):
    @classmethod
    def create_test_inventory_models(cls):
        inv_models.Machine(machine_name="Test Machine",
                                unique_id="T_M",
                                manufacturer="Langston",
                                estimated_value="200000",
                                commissioning_date=datetime.date.today() \
                                - datetime.timedelta(days=500),
                                ).save()

        inv_models.Section(
            unique_id="T_SE",
            section_name= "Test Section",
            machine=inv_models.Machine.objects.get(pk="T_M")
        ).save()

        inv_models.SubUnit(unique_id="T_S",
                unit_name="Test SubUnit",
                machine=inv_models.Machine.objects.get(pk="T_M"),
                section=inv_models.Section.objects.get(pk="T_SE")).save()


        inv_models.SubAssembly(unique_id="T_SA",
                    unit_name="Test SubAssembly",
                    subunit=inv_models.SubUnit.objects.get(pk="T_S",
                    section=inv_models.Section.objects.get(pk="T_SE"),
                    machine=inv_models.Machine.objects.get(pk="T_M"))).save()


        inv_models.Component(unique_id="T_C",
                            component_name="Test Component",
                            subunit=inv_models.SubUnit.objects.get(pk="T_S"),
                            section=inv_models.Section.objects.get(pk="T_SE"),
                            machine=inv_models.Machine.objects.get(pk="T_M"),
                            subassembly=inv_models.SubAssembly.objects.get(pk="T_SA")
                            ).save()


        inv_models.Category(name="Test Category",
                            description="Test Description").save()

        inv_models.InventoryItem(serial_number="100",
                                name="Test Inventory Item",
                                order_number=1,
                                quantity=100,
                                unit="ea",
                                order_date=datetime.date.today(),
                                category=inv_models.Category.objects.get(
                                    name="Test Category"
                                ),
                                supplier="Test Supplier",
                                unit_price=0.1,
                                min_stock_level=20,
                                reorder_quantity=200).save()

        inv_models.Order(order_number="100",
                        description="Test Description",
                        quantity=100,
                        unit_price=0.1,
                        manufacture_date=datetime.date.today(),
                        flute_profile="a",
                        liner="kraft",
                        layers=1,
                        delivery_date=datetime.date.today() + \
                            datetime.timedelta(days=5),
                        customer="Test Customer",
                        production_status="planned",
                        delivery_status="storage").save()


    @classmethod
    def create_test_checklist(cls):
        if inv_models.Machine.objects.all().count() == 0:
            cls.create_test_inventory_models()
            
        if Account.objects.all().count() == 0:
            cls.create_dummy_accounts()

        cls._checklist_data = {
            "title": "Test Checklist",
            "creation_date": datetime.date.today(),
            "last_completed_date": None,
            "estimated_time": "0030",
            "start_time": "0900",
            "machine": inv_models.Machine.objects.get(pk="T_M"),
            "subunit": inv_models.SubUnit.objects.get(pk="T_S"),
            "subassembly": None,
            "resolver": Account.objects.first(),
            "category": "electrical",
            "frequency": "daily"
        }
        ch_models.Checklist(**cls._checklist_data).save()


    @classmethod
    def create_test_jobcards(cls):
        if inv_models.Machine.objects.all().count() == 0:
            cls.create_test_inventory_models()

        if Account.objects.all().count() == 0:
            cls.create_dummy_accounts() 

        common_data = {"description": "Test Description",
                    "creation_epoch": datetime.date.today(),
                    "resolver": Account.objects.first(),
                    "estimated_time": "0030",
                    "completed": False,
                    "machine": inv_models.Machine.objects.first(),
                    "subunit": inv_models.SubUnit.objects.first()
                    }
        planned_data = common_data
    
        p = jb_models.PlannedJob(**planned_data)
        p.scheduled_for = timezone.now()
        p.save()

        breakdown_data = common_data
        breakdown_data["requested_by"] = Account.objects.first()
        jb_models.Breakdown(**breakdown_data).save()     

    @classmethod
    def create_dummy_accounts(cls):
        Account(username= "Test User",
                first_name="Test",
                last_name="User",
                password="test123",
                role="artisan").save()

        Account(username= "Test Admin User",
                first_name="Test",
                last_name="User",
                password="test123",
                role="admin").save()
