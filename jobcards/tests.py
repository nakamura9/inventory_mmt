import datetime
import json

from django.test import TestCase, Client
from django.shortcuts import reverse
from django.utils import timezone

from common_base.tests import TestDataMixin
from inventory_mmt import settings
from .models import WorkOrder, PreventativeTask
from common_base.models import Account, Category
from inv.models import *


class ViewTests(TestCase, TestDataMixin):
    @classmethod
    def setUpClass(cls):
        super(ViewTests, cls).setUpClass()
        cls.client = Client()
        cls.today = datetime.date.today()
        settings.TEST_CONDITIONS = True

    @classmethod
    def setUpTestData(cls):
        super(ViewTests, cls).setUpTestData()
        cls.create_dummy_accounts()
        cls.create_test_inventory_models()

    def test_new_work_order_get(self):
        response = self.client.get(reverse("jobcards:new-work-order"))
        self.assertEqual(response.status_code, 200)

    def test_new_work_order_post(self):
        response = self.client.post(reverse("jobcards:new-work-order"),
            {"machine": Machine.objects.first().pk,
            "section": Section.objects.first().pk,
            "type": Category.objects.first().pk,
            "description": "test description",
            "execution_date":self.today.strftime("%m/%d/%Y"),
            "estimated_labour_time":"1:00:00",
            "assigned_to": Account.objects.first().pk,
            "priority": "low"})
        self.assertEqual(response.status_code, 302)

    def test_work_order_list_get(self):
        self.create_test_workorders()
        response = self.client.get(reverse("jobcards:work-order-list"))
        self.assertEqual(response.status_code, 200)

    def test_complete_work_order_get(self):
        self.create_test_workorders()
        response = self.client.get(reverse("jobcards:complete-work-order",
            kwargs={"pk": WorkOrder.objects.first().pk}))
        self.assertEqual(response.status_code, 200)

    def test_complete_work_order_post(self):
        self.create_test_workorders()
        response = self.client.post(reverse("jobcards:complete-work-order",
            kwargs={"pk": WorkOrder.objects.first().pk}),
                {"resolver_action": "test resolver action",
                "actual_labour_time": "1:00:00",
                "downtime": "1:00:00",
                "completion_date": self.today.strftime("%m/%d/%Y")})
        self.assertEqual(response.status_code, 302)

    def test_edit_work_order_get(self):
        self.create_test_workorders()
        response = self.client.get(reverse("jobcards:edit-work-order",
            kwargs={"pk": WorkOrder.objects.first().pk}))
        self.assertEqual(response.status_code, 200)

    def test_edit_work_order_post(self):
        self.create_test_workorders()
        response = self.client.post(reverse("jobcards:edit-work-order",
            kwargs={"pk": WorkOrder.objects.first().pk}),
            {"subunit": SubUnit.objects.first().pk,
            "machine": Machine.objects.first().pk,
            "section": Section.objects.first().pk,
            "type": Category.objects.first().pk,
            "description": "test description",
            "execution_date":self.today.strftime("%m/%d/%Y"),
            "estimated_labour_time":"1:00:00",
            "assigned_to": Account.objects.first().pk,
            "priority": "low"})
        self.assertEqual(response.status_code, 302)

    def test_accept_job(self):
        self.create_test_workorders()
        pk = WorkOrder.objects.first().pk
        response = self.client.post(reverse("jobcards:accept-job"),
            {"pk": pk})
        resp = json.loads(response.content)
        self.assertTrue(resp["accepted"])
        wo = WorkOrder.objects.first()
        self.assertEqual(wo.status, "accepted")

    def test_work_order_detail(self):
        self.create_test_workorders()
        response = self.client.get(reverse("jobcards:work-order-detail",
            kwargs={"pk": WorkOrder.objects.first().pk}))
        self.assertEqual(response.status_code, 200)

    def test_approve_job(self):
        self.create_test_workorders()
        response = self.client.get(reverse("jobcards:approve-job",
            kwargs={"pk": WorkOrder.objects.first().pk}))
        self.assertEqual(response.status_code, 302)

    def test_decline_job(self):
        self.create_test_workorders()
        self.client.login(username="Test User", password="test123")
        response = self.client.post(reverse("jobcards:decline-job"),
            {"job": WorkOrder.objects.first().pk,
            "reason": "Some test reason"})
        resp = json.loads(response.content)
        self.assertTrue(resp["success"])
        wo = WorkOrder.objects.first()
        self.assertEqual(wo.comments.count(), 1)

    def test_transfer_job(self):
        self.create_test_workorders()
        self.client.login(username="Test User", password="test123")
        response = self.client.post(reverse("jobcards:decline-job"),
            {"job": WorkOrder.objects.first().pk,
            "reason": "Some test reason"})
        resp = json.loads(response.content)
        self.assertTrue(resp["success"])
        wo = WorkOrder.objects.first()
        self.assertEqual(wo.comments.count(), 1)

    def test_new_preventatitve_task_get(self):
        response = self.client.get(reverse("jobcards:new-preventative-task"))
        self.assertEqual(response.status_code, 200)

    def test_new_preventative_task_post(self):
        response = self.client.post(reverse("jobcards:new-preventative-task"),
            {"machine": Machine.objects.first().pk,
            "section": Section.objects.first().pk,
            "type": Category.objects.first().pk,
            "description": "test description",
            "scheduled_for":self.today.strftime("%m/%d/%Y"),
            "frequency": "once",
            "estimated_labour_time":"1:00:00",
            "estimated_downtime": "1:00:00",
            "tasks[]": ["task one", "task two"],
            "assignments[]": ["Test User"],
            "spares[]": [Spares.objects.first().stock_id]})
        self.assertEqual(response.status_code, 302)

    def test_complete_preventative_task_get(self):
        self.create_test_preventative_task()
        response = self.client.get(reverse("jobcards:complete-preventative-task",
            kwargs={"pk":PreventativeTask.objects.first().pk}))
        self.assertEqual(response.status_code, 200)

    def test_complete_preventative_task_post(self):
        self.create_test_preventative_task()
        response = self.client.post(reverse("jobcards:complete-preventative-task",
            kwargs={"pk":PreventativeTask.objects.first().pk}),
                {"actual_downtime": "1:00:00",
                "completed_date": self.today.strftime("%m/%d/%Y"),
                "feedback": "test feedback"})
        self.assertEqual(response.status_code, 302)

    def test_edit_preventative_task_get(self):
        self.create_test_preventative_task()
        response = self.client.get(reverse("jobcards:edit-preventative-task",
            kwargs={"pk":PreventativeTask.objects.first().pk}))
        self.assertEqual(response.status_code, 200)
    
    def test_edit_preventative_task_post(self):
        self.create_test_preventative_task()
        response = self.client.get(reverse("jobcards:preventative-task-detail",
            kwargs={"pk":PreventativeTask.objects.first().pk}),
                {"machine": Machine.objects.first().pk,
                "section": Section.objects.first().pk,
                "type": Category.objects.first().pk,
                "description": "test description",
                "scheduled_for":self.today.strftime("%m/%d/%Y"),
                "frequency": "weekly",
                "estimated_labour_time":"1:00:00",
                "estimated_downtime": "1:00:00",
                "tasks[]": ["task three"]})
        self.assertEqual(response.status_code, 200)

    def test_preventative_task_detail(self):
        self.create_test_preventative_task()
        response = self.client.get(reverse("jobcards:preventative-task-detail",
            kwargs={"pk":PreventativeTask.objects.first().pk}))
        self.assertEqual(response.status_code, 200)

    def test_delete_preventative_task(self):
        self.create_test_preventative_task()
        self.client.get(reverse("jobcards:delete-preventative-task",
            kwargs={"pk": PreventativeTask.objects.first().pk}))
        self.assertEqual(PreventativeTask.objects.all().count(), 0)

    def test_accept_preventative_task(self):
        self.create_test_preventative_task()
        response =self.client.post(reverse("jobcards:accept-p-task"),
            {"pk": PreventativeTask.objects.first().pk,
            "resolver": "Test User"})
        resp = json.loads(response.content)
        self.assertTrue(resp["accepted"])
        p_task = PreventativeTask.objects.first()
        self.assertEqual(p_task.assignments_accepted.count(), 1)


    
    

