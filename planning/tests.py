import calendar

from django.test import TestCase, Client
from django.shortcuts import reverse

from calendar_objects import *
from common_base.tests import TestDataMixin
from inv.models import Machine, RunData
from jobcards.models import  WorkOrder


class ViewTests(TestCase, TestDataMixin):
    @classmethod
    def setUpTestData(cls):
        super(ViewTests, cls).setUpTestData()
        cls.create_dummy_accounts()
        cls.create_test_checklist()
        cls.create_test_preventative_task()
        cls.create_test_workorders()

    @classmethod
    def setUpClass(cls):
        super(ViewTests, cls).setUpClass()
        cls.today = datetime.date.today()
        

    def get_week_from_date(self):
        c = calendar.Calendar()
        arr = c.monthdatescalendar(self.today.year, self.today.month)
        for row in arr:
            if self.today in row:
                self.week = arr.index(row)

    def test_maintenance_day_view_get(self):
        response = self.client.get(reverse("planning:maintenance-day",
            kwargs={"year": self.today.year,
                    "month": self.today.month,
                    "day": self.today.day}))

        self.assertEqual(response.status_code, 200)
        if self.today.weekday() < 5: #wont work on weekends
            self.assertEqual(len(response.context["day"].agenda), 2)

    def test_maintenance_day_view_filtered(self):
        response = self.client.get(reverse("planning:maintenance-day",
            kwargs={"year": self.today.year,
                    "month": self.today.month,
                    "day": self.today.day}),
                {"checklists": "on",
                "date": self.today.strftime("%m/%d/%Y")})

        self.assertEqual(response.status_code, 200)
        if self.today.weekday() < 5: #wont work on weekends
            self.assertEqual(len(response.context["day"].agenda), 1)

    def test_maintenance_week_view_get(self):
        self.get_week_from_date()
        response = self.client.get(reverse("planning:maintenance-week",
            kwargs={"year": self.today.year,
                    "month": self.today.month,
                    "week": self.week }))

        self.assertEqual(response.status_code, 200)
        if self.today.weekday() < 5: #wont work on weekends
            self.assertEqual(len(
                response.context["week"].week_agenda[
                    self.today.weekday()].agenda), 2)
        
    def test_maintenance_week_view_filtered(self):
        self.get_week_from_date()
        response = self.client.get(reverse("planning:maintenance-week",
            kwargs={"year": self.today.year,
                    "month": self.today.month,
                    "week": self.week }),
                {"year": self.today.year,
                "month": self.today.month,
                "week": self.week,
                "resolver": "Test Admin User",
                "machine": ""})# no resolver
        #needs fixing
        self.assertEqual(response.status_code, 200)
        if self.today.weekday() < 5: #wont work on weekends
            self.assertEqual(len(
                response.context["week"].week_agenda[
                    self.today.weekday()].agenda), 0)

    def test_maintenance_month_view_get(self):
        response = self.client.get(reverse("planning:maintenance-month"))
        self.assertEqual(response.status_code, 200)

    def test_maintenance_month_view_get_w_kwargs(self):
        response = self.client.get(reverse("planning:maintenance-month",
            kwargs={"year": self.today.year,
                    "month": self.today.month}))
        self.assertEqual(response.status_code, 200)

    def test_maintenance_month_view_filtered(self):
        response = self.client.get(reverse("planning:maintenance-month",
            kwargs={"year": self.today.year,
                    "month": self.today.month}),
            data={"year": self.today.year,
                    "month": self.today.month,
                    "resolver": "Test User",
                    "machine": ""})
        self.assertEqual(response.status_code, 200)

    def test_production_day_view_get(self):
        response = self.client.get(reverse("planning:production-day",
            kwargs={"year": self.today.year,
                    "month": self.today.month,
                    "day": self.today.day}))

        self.assertEqual(response.status_code, 200)

    def test_production_week_view_get(self):
        self.get_week_from_date()
        response = self.client.get(reverse("planning:production-week",
            kwargs={"year": self.today.year,
                    "month": self.today.month,
                    "week": self.week}))

        self.assertEqual(response.status_code, 200)

    def test_production_month_view_get(self):
        response = self.client.get(reverse("planning:production-month",
            kwargs={"year": self.today.year,
                    "month": self.today.month}))

        self.assertEqual(response.status_code, 200)

class CalendarObjectsTests(TestCase, TestDataMixin):
    @classmethod
    def setUpTestData(cls):
        super(CalendarObjectsTests, cls).setUpTestData()
        cls.create_dummy_accounts()
        cls.create_test_checklist()
        cls.create_test_preventative_task()
        cls.create_test_workorders()

    @classmethod
    def setUpClass(cls):
        super(CalendarObjectsTests, cls).setUpClass()
        cls.today = datetime.date.today()
        
    def get_week_from_date(self):
        c = calendar.Calendar()
        arr = c.monthdatescalendar(self.today.year, self.today.month)
        for row in arr:
            if self.today in row:
                self.week = arr.index(row)

    def test_production_element(self):
        mech = Machine.objects.first()
        mech.run_data.add(RunData.objects.first())
        pe = ProductionElement(mech, self.today)
        self.assertEqual(pe.planned_downtime, 1.0)
        if self.today.weekday() < 3:
            self.assertEqual(pe.running_hours, 1.0)
        else:
            self.assertEqual(pe.running_hours, 0.0)
        self.assertEqual(pe.net_up_time, 0)
