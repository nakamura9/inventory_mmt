# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import os
import random

from django.shortcuts import reverse
from django.test import TestCase, Client
from django.utils import timezone

from checklists import models as ch_models
from inv import models as inv_models
from jobcards import models as jb_models
from . import models
from .utilities import *
from inventory_mmt import settings

class TestDataMixin(object):
    """This class is used to provide test data for other applications, especially those whose tests have multiple dependancies.
    models:
    Machine, Section, SubUnit, SubAssembly, Component, Category, Inventory_item, Order.
    
    classmethods:
        create_dummy_accounts
        create_test_checklist"""

    @classmethod
    def create_test_inventory_models(cls):
        inv_models.Spares(name="test spares",
                            description="test description",
                            stock_id="01").save()
        inv_models.Machine(machine_name="Test Machine",
                                unique_id="T_M",
                                manufacturer="Langston",
                                commissioning_date=datetime.date.today() \
                                - datetime.timedelta(days=500),
                                ).save()
        inv_models.RunData(
            start_date = datetime.date.today(),
            end_date = datetime.date.today() + datetime.timedelta(days=7),
            run_days = 3,
            run_hours = 1,
            monday=True,
            tuesday=True,
            wednesday=True).save()
                        
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
            "estimated_time": datetime.timedelta(hours=1),
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
    def create_test_preventative_task(cls):
        jb_models.PreventativeTask(
            machine= inv_models.Machine.objects.get(pk="T_M"),
            section= inv_models.Section.objects.get(pk="T_SE"),
            subunit=inv_models.SubUnit.objects.get(pk="T_S"),
            subassembly=inv_models.SubAssembly.objects.first(),
            component=inv_models.Component.objects.first(),
            description="Some description...",
            frequency="once",
            estimated_labour_time=datetime.timedelta(seconds=3600),
            estimated_downtime=datetime.timedelta(seconds=3600),
            scheduled_for=datetime.date.today(),
            actual_downtime=datetime.timedelta(seconds=3600),
            completed_date=datetime.date.today()).save()

    @classmethod
    def create_test_workorders(cls):
        jb_models.WorkOrder(
            type=models.Category.objects.first(),
            machine= inv_models.Machine.objects.get(pk="T_M"),
            section= inv_models.Section.objects.get(pk="T_SE"),
            subunit=inv_models.SubUnit.objects.get(pk="T_S"),
            subassembly=inv_models.SubAssembly.objects.first(),
            component=inv_models.Component.objects.first(),
            description="Some description...",
            execution_date=datetime.date.today(),
            completion_date=datetime.date.today(),
            estimated_labour_time=datetime.timedelta(seconds=3600),
            assigned_to=models.Account.objects.first(),
            priority="low",
            status="requested",
            resolver_action= "Some action...",
            actual_labour_time=datetime.timedelta(seconds=3600),
            downtime=datetime.timedelta(seconds=3600)).save()
        job = jb_models.WorkOrder.objects.first()
        job.spares_issued.add(inv_models.Spares.objects.first())
        job.spares_returned.add(inv_models.Spares.objects.first())
    
    names = ["printer", "bearing", "nut", "shaft", "unit",
        "slotter", "gasket", "gearbox", "panel",
        "HMI", "PLC", "compressor", "fitting", "drum",
        "roller", "mount"]

    times = [360, 1800, 3600, 7200, 10800]
    def create_n_equipment(self, n):
        # n machines
        # 2n sections
        # 4n subunits 
        #etc
        for i in range(n):
            m_pk = "0"+str(i)
            inv_models.Machine(
                machine_name=random.choice(self.names),
                unique_id= m_pk,
                manufacturer="Test",
                commissioning_date=datetime.date.today() \
                    - datetime.timedelta(days=500)).save()

            for j in range(2):
                s_pk = m_pk +"0"+ str(j)
                inv_models.Section(
                    unique_id=s_pk,
                    section_name= random.choice(self.names) + " section",
                    machine=inv_models.Machine.objects.get(
                        pk="0"+str(i))).save()
                        
                for k in range(2):
                    su_pk = s_pk+"0"+ str(k)
                    inv_models.SubUnit(
                    unique_id=su_pk,
                    unit_name=random.choice(self.names) + " subunit",
                    machine=inv_models.Machine.objects.get(pk=m_pk),
                    section=inv_models.Section.objects.get(
                        pk=s_pk)).save()

                    for l in range(4):
                        sa_pk = su_pk +"0"+str(l)
                        inv_models.SubAssembly(
                            unique_id=sa_pk,
                            unit_name=random.choice(self.names) + " subassembly",
                            subunit=inv_models.SubUnit.objects.get(pk=su_pk),
                            section=inv_models.Section.objects.get(pk=s_pk),
                            machine=inv_models.Machine.objects.get(
                                pk=m_pk)).save()

                        for m in range(4):
                            inv_models.Component(
                                unique_id=sa_pk +"0"+ str(m),
                                component_name=random.choice(self.names) +\
                                    " component",
                                subunit=inv_models.SubUnit.objects.get(
                                    pk=su_pk),
                                section=inv_models.Section.objects.get(
                                    pk=s_pk),
                                machine=inv_models.Machine.objects.get(pk=m_pk),
                                subassembly=inv_models.SubAssembly.objects.get(
                                    pk=sa_pk)
                            ).save()

    def random_date(self, start, end):
        delta = abs((end - start).days)
        
        choice = random.randint(0, delta)
        return start + datetime.timedelta(days=choice)

    def random_machine(self):
        return self.get_random_object(inv_models.Machine)

    def random_section(self):
        return self.get_random_object(inv_models.Section)

    def random_subunit(self):
        return self.get_random_object(inv_models.SubUnit)

    def random_subassembly(self):
        return self.get_random_object(inv_models.SubAssembly)

    def random_component(self):
        return self.get_random_object(inv_models.Component)

    def random_account(self):
        return self.get_random_object(Account)

    def get_random_object(self, model):
        objs = [obj for obj in model.objects.all()]
        return random.choice(objs)
    
    def create_n_work_orders(self, n, start, end):
        for i in range(n):
            d = self.random_date(start, end)
            jb_models.WorkOrder(
                type=models.Category.objects.first(),
                machine= self.random_machine(),
                section= self.random_section(),
                subunit=self.random_subunit(),
                subassembly=self.random_subassembly(),
                component=self.random_component(),
                description="Some description...",
                execution_date=d,
                completion_date=d,
                estimated_labour_time=datetime.timedelta(
                    seconds=random.choice(self.times)),
                assigned_to=self.random_account(),
                priority="low",
                status="requested",
                resolver_action= "Some action...",
                actual_labour_time=datetime.timedelta(
                    seconds=random.choice(self.times)),
                downtime=datetime.timedelta(
                    seconds=random.choice(self.times))).save()

    def create_n_preventative_tasks(self, n, start, end):
        frequencies = ["once", "weekly", "monthly"]
        for i in range(n):
            d = self.random_date(start, end)
            jb_models.PreventativeTask(
                machine= self.random_machine(),
                section= self.random_section(),
                subunit=self.random_subunit(),
                subassembly=self.random_subassembly(),
                component=self.random_component(),
                description="Some description...",
                frequency=random.choice(frequencies),
                estimated_labour_time=datetime.timedelta(
                    seconds=random.choice(self.times)),
                estimated_downtime=datetime.timedelta(
                    seconds=random.choice(self.times)),
                scheduled_for=d,
                actual_downtime=datetime.timedelta(
                    seconds=random.choice(self.times)),
                completed_date=d).save()

    def create_n_checklists(self, n, start, end):
        for i in range(n):
            d = self.random_date(start, end)
            ch_models.Checklist(**{
               "title": "Test Checklist",
                "creation_date": d,
                "last_completed_date": random.choice([None, d]),
                "estimated_time": datetime.timedelta(
                    seconds=random.choice(self.times)),
                "start_time": datetime.time(8,30),
                "machine": self.random_machine(),
                "section": self.random_section(),
                "subunit": self.random_subunit(),
                "subassembly": self.random_subassembly(),
                "component": self.random_component(),
                "resolver": self.random_account(),
                "category": "electrical",
                "frequency": random.choice(["daily", "weekly", "monthly"])
            }).save()
    
    @classmethod
    def create_dummy_accounts(cls):
        regular = models.Account(username= "Test User",
                first_name="Test",
                last_name="User",
                role="artisan")
        regular.set_password("test123")#LIFE SAVER !!!
        regular.save()

        special = models.Account(username= "Test Admin User",
                first_name="Test",
                last_name="User",
                role="admin")
        special.set_password("test123")
        special.save()


class TestUtilities(TestCase, TestDataMixin):
    """Tests the utilities functions.
    """
    @classmethod
    def setUpTestData(cls):
        cls.create_dummy_accounts()
        cls.create_test_inventory_models()
        cls.create_test_workorders()
        cls.today = datetime.datetime.today()
    
    def setUp(self):
        self.status_store = {"messages":[],
                    "successful": 0,
                    "errors": 0,
                    "start": 0.0,
                    "stop": 0.0,
                    "running": False,
                    "finished": False,
                    "file_length": 0,
                    }

    def test_time_choices(self):
        data = time_choices("13:00:00", "20:00:00", "00:15:00")
        self.assertIsInstance(data, list)

    def test_filter_by_dates(self):
        """test with start only, stop only or both"""
        wos = jb_models.WorkOrder.objects.all()
        queryset = filter_by_dates(wos, 
                        self.today - datetime.timedelta(days=1),
                        self.today + datetime.timedelta(days=1))
        self.assertEqual(queryset.count(), 1) # one 

        queryset = filter_by_dates(wos, 
            self.today + datetime.timedelta(days=1),
            self.today + datetime.timedelta(days=3))
        self.assertEqual(queryset.count(), 0) #empty

    def test_role_test(self):
        """tests function for determining the role of a user requesting a page"""
        settings.TEST_CONDITIONS = False
        self.assertTrue(role_test(Account.objects.get(
            username ="Test Admin User")))
        self.assertFalse(role_test(Account.objects.get(
            username="Test User")))
        settings.TEST_CONDITIONS = True

    def test_parse_spares_file(self):
        """will need to create a sample a spares file"""
        fil = os.path.join("common_base", "test_files", "test_spares.csv")
        parse_spares_file(self.status_store, fil)
        self.assertEqual(self.status_store["errors"], 0)
        self.assertEqual(self.status_store["successful"],99)
        self.assertTrue(self.status_store["finished"])

    def test_parse_inventory_file(self):
        """will need to create a dummpy inventory_file"""
        fil = os.path.join("common_base", "test_files", "test_inv.csv")
        inv_models.Machine(
            unique_id="01",
            machine_name="test machine",
            manufacturer="someone").save()
        parse_file(self.status_store, fil)
        self.assertEqual(self.status_store["errors"], 0)
        self.assertEqual(self.status_store["successful"], 98)


class TestViews(TestCase):
    """Used to test content created by the category form."""

    @classmethod
    def setUpClass(cls):
        super(TestViews, cls).setUpClass()
        cls.client = Client()
            
    def test_sign_up_get(self):
        """get sign up page"""
        response = self.client.get(reverse("sign_up"))
        self.assertEqual(response.status_code, 200)

    def test_sign_up_post(self):
        """create account page"""
        response = self.client.post(reverse("sign_up"),
            {
                "username": "tester",
                "role": "artisan",
                "first_name": "unit",
                "last_name": "test",
                "password": "test123"
                })
        self.assertEqual(response.status_code, 302)

    def test_logout(self):
        """logs in and then checks with the session that no user is present"""
        self.client.login(username="Test User", password="test123")
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)

    def test_about_view(self):
        response = self.client.get(reverse("about"))
        self.assertEqual(response.status_code, 200)

    def test_login_get(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_login_post(self):
        response = self.client.post(reverse("login"), {"name": "Test User",
                                                        "pwd": "test123"})
        self.assertEqual(response.status_code, 302)


class TestModels(TestCase, TestDataMixin):
    """Tests the common models.
    
    models: Comment, Task, Account, Category"""
    
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

    def test_create_category(self):
        category = models.Category.objects.create(created_for="work_order",
                                                    name="Electrical",
                                                    description="Some description")
        self.assertIsInstance(category, models.Category)