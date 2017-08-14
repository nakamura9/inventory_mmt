from django.test import TestCase
from django.test import Client
from checklists import models
import datetime
from inv import models as inv_models
from common_base.models import Account
from common_base.tests import TestDataMixin

class ModelTests(TestCase, TestDataMixin):
    @classmethod
    def setUpTestData(cls):
        super(ModelTests, cls).setUpTestData()
        cls.create_test_inventory_models()
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
        models.Checklist(**cls._checklist_data).save()

    def test_create_comment(self):
        comment = models.Comment.objects.create(
            checklist=models.Checklist.objects.get(title="Test Checklist"),
            author=Account.objects.first(),
            content="Test Comment"
        )
        self.assertIsInstance(comment, models.Comment)


    def test_create_checklist(self):
        self._checklist_data["title"] = "Unit Test Checklist"
        check = models.Checklist.objects.create(**self._checklist_data)
        self.assertIsInstance(check, models.Checklist)

    def test_create_task(self):
        task = models.Task.objects.create(
                checklist=models.Checklist.objects.get(title="Test Checklist"),
                    task_number=1, description="A Test Checklist Task")
        self.assertIsInstance(task, models.Task)



    """def test_tasks_associated_with_checklists(self):
        pass

    def test_comments_associated_with_checklists(self):
        pass
    """


    def test_checklist_properties(self):
        check = models.Checklist.objects.get(title="Test Checklist")
        
        self.assertTrue(check.is_open)
        check.last_completed_date = datetime.date.today()
        #check if the checklist remains open
        self.assertFalse(check.is_open)
        #check if the next day for the checklist is tomorrow
        self.assertEqual(check.next, datetime.date.today() + \
                        datetime.timedelta(days=1))

