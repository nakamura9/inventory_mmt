# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import random

from django.shortcuts import reverse
from django.test import TestCase, Client
from django.utils import timezone

from checklists import models as ch_models
from inv import models as inv_models
from jobcards import models as jb_models
from . import models
from .utilities import time_choices


class TestUtilities(TestCase):
    """Tests the utilities functions.
    
    ajaxRequired decorator untested because the function is copied from the github community and has been tested by the author."""

    def test_time_choices(self):
        data = time_choices("13:00:00", "20:00:00", "00:15:00")
        self.assertIsInstance(data, list)

    

class TestViews(TestCase):
    """Used to test content created by the category form."""

    @classmethod
    def setUpClass(cls):
        super(TestViews, cls).setUpClass()
        cls.client = Client()
    
    def test_post_check_and_delete_category(self):
        #delete view for category not yet implemented
        response = self.client.post(reverse("inventory:new-category"),
                                    data={
                                    "created_for": "work_order",
                                    "name":"Posted Test Category",
                                    "description": "Posted Test Description"
                                        })
        
        self.assertIsInstance(models.Category.objects.get(
                            name="Posted Test Category"), models.Category)
        


class TestDataMixin(object):
    """This class is used to provide test data for other applications, especially those whose tests have multiple dependancies.
    models:
    Machine, Section, SubUnit, SubAssembly, Component, Category, Inventory_item, Order.
    
    classmethods:
        create_dummy_accounts
        create_test_checklist"""

    @classmethod
    def create_test_inventory_models(cls):
        inv_models.Machine(machine_name="Test Machine",
                                unique_id="T_M",
                                manufacturer="Langston",
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


        models.Category(created_for="work_order",
                            name="Test Category",
                            description="Test Description").save()

        """inv_models.InventoryItem(serial_number="100",
                                name="Test Inventory Item",
                                order_number=1,
                                quantity=100,
                                unit="ea",
                                order_date=datetime.date.today(),
                                category=models.Category.objects.get(
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
                        delivery_status="storage").save()"""


    @classmethod
    def create_test_checklist(cls):
        if inv_models.Machine.objects.all().count() == 0:
            cls.create_test_inventory_models()
            
        if models.Account.objects.all().count() == 0:
            cls.create_dummy_accounts()

        cls._checklist_data = {
            "title": "Test Checklist",
            "creation_date": datetime.date.today(),
            "last_completed_date": None,
            "estimated_time": datetime.timedelta(hours=1, minutes=30),
            "start_time": datetime.time(15,30),
            "machine": inv_models.Machine.objects.get(pk="T_M"),
            "section": inv_models.Section.objects.get(pk="T_SE"),
            "subunit": inv_models.SubUnit.objects.get(pk="T_S"),
            "subassembly": None,
            "resolver": models.Account.objects.first(),
            "category": "electrical",
            "frequency": "daily"
        }
        ch_models.Checklist(**cls._checklist_data).save()


    @classmethod
    def create_test_workorders(cls):
        jb_models.WorkOrder(type=models.Category.objects.first(),
                            machine= inv_models.Machine.objects.get(pk="T_M"),
                            section= inv_models.Section.objects.get(pk="T_SE"),
                            subunit=inv_models.SubUnit.objects.get(pk="T_S"),
                            subassembly=inv_models.SubAssembly.objects.first(),
                            component=inv_models.Component.objects.first(),
                            description="Some description...",
                            execution_date=datetime.date.today(),
                            estimated_labour_time="00:30",
                            assigned_to=models.Account.objects.first(),
                            priority="low",
                            status="requested",
                            resolver_action= "Some action...",
                            actual_labour_time="00:30").save()
        jb_models.WorkOrder.first().spares_issued_set.add(Spares.objects.first()).save()
        jb_models.WorkOrder.first().spares_returned_set.add(Spares.objects.first()).save()

    @classmethod
    def create_dummy_accounts(cls):
        models.Account(username= "Test User",
                first_name="Test",
                last_name="User",
                password="test123",
                role="artisan").save()

        models.Account(username= "Test Admin User",
                first_name="Test",
                last_name="User",
                password="test123",
                role="admin").save()


class TestModels(TestCase, TestDataMixin):
    """Tests the common models.
    
    models: Comment, Task, Account"""
    def test_create_account(self):
        models.Account(username= "Test User",
                first_name="Test",
                last_name="User",
                password="test123",
                role="artisan").save()

        self.assertIsInstance(models.Account.objects.get(username="Test User"),
                                models.Account)

    def test_create_comment(self):
        self.create_dummy_accounts()
        comment = models.Comment.objects.create(
            created_for= "checklist",
            author=models.Account.objects.first(),
            content="Test Comment"
        )
        self.assertIsInstance(comment, models.Comment)

    def test_create_task(self):
        task = models.Task.objects.create(
                created_for="checklist",
                task_number=1, description="A Test Checklist Task")
        self.assertIsInstance(task, models.Task)
