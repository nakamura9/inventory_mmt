from django.test import TestCase, Client
from calendar_objects import *
from common_base.tests import TestDataMixin
from inv.models import Order


class CalendarObjectsTests(TestCase, TestDataMixin):
    @classmethod
    def setUpTestData(cls):
        super(CalendarObjectsTests, cls).setUpTestData()
        cls.create_test_checklist()# will also create dummy inventory models
        cls.create_test_jobcards()


    def test_production_day_agenda(self):
        day = ProductionDay(datetime.date.today())
        day.get_agenda()
        self.assertTrue(Order.objects.first() in day.agenda)
        

    def test_maintenance_day_agenda(self):
        day = MaintenanceDay(datetime.date.today())
        day.get_agenda()
        self.assertFalse(Checklist.objects.first() in day.agenda)
        self.assertTrue(PlannedJob.objects.first() in day.agenda)

    def test_week(self):
        today = datetime.date.today()
        _month = calendar.Calendar().monthdatescalendar(today.year, 
                                                        today.month)
        for _week in _month:
            for day in _week:
                if day == today:
                    week_number = _month.index(_week)

        week = Week(today.year, today.month, week_number, MaintenanceDay)
        week.get_week_agenda()
        self.assertTrue(week.week_agenda != [])


    def test_month(self):
        today = datetime.date.today()
        month = Month(today.year, today.month, ProductionDay)
        month.get_month_agenda()
        self.assertTrue(month.month_agenda != [])
        
