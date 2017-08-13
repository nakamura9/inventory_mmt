from django.test import TestCase
from django.test import Client
from checklists import models
import datetime
from inv import models as inv_models

class ModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        inv_models.objects.create(machine_name="Checklist Test Machine",
                                unique_id="C_T_M",
                                manufacturer="Langston",
                                estimated_value="200000",
                                commissioning_date=datetime.date.today() - datetime.timedelta(years=5),
                                )
        inv_models.SubUnit.objects.create(unique_id="C_T_S",
                                        unit_name="Checklist Test SubUnit",
                                        machine=inv_models.Machine.objects.get(pk="C_T_M"))

        inv_models.SubAssembly.objects.create(unique_id="C_T_SA",
                                            unit_name="Checklist_Test_SubAssembly",
                                            subunit=inv_models.SubUnit.objects.get(pk="C_T_S",
                                            machine=inv_models.Machine.objects.get(pk="C_T_M")))


        cls._checklist_data = {
            "title": "Test Checklist",
            "creation_date": datetime.date.today(),
            "last_completed_date": None,
            "estimated_time": "0030",
            "start_time": "0900",
            "machine": inv_models.objects.get("C_T_M"),
            "subunit": inv_models.objects.get("C_T_S"),
            "subassembly": None,
            "resolver": inv_models.Account.objects.first(),
            "category": "electrical",
            "frequency": "daily"
        }
        models.Checklist.objects.create(**cls._checklist_data)

    def test_create_comment(self):
        models.Comment.objects.create(
            checklist=models.Checklist.objects.get(title="Test Checklist"),
            author=inv_models.Account.objects.first(),
            content="Test Comment"
        )


    def test_create_checklist(self):
        self._checklist_data["title"] = "Unit Test Checklist"
        models.Checklist(**self._checklist_data).save()
        self.assertTrue(isinstance(
            models.Checklist.objects.get(title="Unit Test Checklist"), 
            models.Checklist))

    def test_create_task(self):
        models.Task(checklist=models.Checklist.objects.get(title="Test Checklist"),
                    task_number=1,
                    description="A Test Checklist Task")

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

