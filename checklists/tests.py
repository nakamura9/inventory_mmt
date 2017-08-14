from django.test import TestCase
from django.test import Client
from checklists import models
import datetime
from inv import models as inv_models
from common_base.models import Account
from common_base.tests import TestDataMixin
from django.shortcuts import reverse

class ModelTests(TestCase, TestDataMixin):
    @classmethod
    def setUpTestData(cls):
        super(ModelTests, cls).setUpTestData()
        cls.create_test_inventory_models()
        cls.create_dummy_accounts()
        cls.create_test_checklist()
      
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


class TestViews(TestCase, TestDataMixin):
    @classmethod
    def setUpClass(cls):
        super(TestViews, cls).setUpClass()
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        super(TestViews, cls).setUpTestData()
        cls.create_dummy_accounts()
        cls.create_test_checklist()

    def test_inbox(self):
        response = self.client.get(reverse("checklists:inbox"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["message"], "No user logged in")


    """def test_inbox_with_user(self):
        print Account.objects.all()
        response = self.client.get(reverse("checklists:inbox"), 
                                    {"username": "Test User",
                                    "pwd":"test123"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["message"], "Hello Test User")


    def test_inbox_with_jobs(self):
        pass

    def test_inbox_with_planned_jobs(self):
        pass

    def test_inbox_with_checklists(self):
        pass

    """ 

    def test_checklist_detailview(self):
        response = self.client.get(reverse("checklists:checklist_details", 
                                    kwargs={"pk": "Test Checklist"}))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["object"].title, "Test Checklist")


    def test_get_checklist_form(self):
        response = self.client.get(reverse("checklists:create_checklist"))
        self.assertEqual(response.status_code, 200)


    def test_post_checklist_creation_form(self):
        session = self.client.session
        session["tasks"] = ["some test task"]
        session.save()
        response = self.client.post(reverse("checklists:create_checklist"),data=self._checklist_data)

        self.assertEqual(response.status_code, 200)
    
    def test_get_checklist_updateview(self):
        response = self.client.get(reverse("checklists:update_checklist",
                                 kwargs={"pk":"Test Checklist"}))
        self.assertEqual(response.status_code, 200)


    def test_post_checklist_updateview(self):
        session = self.client.session
        session["tasks"] = ["some test task"]
        session.save()
        self._checklist_data["estimated_time"] = "0100"
        response = self.client.post(reverse("checklists:update_checklist",
                                            kwargs={"pk":"Test Checklist"}), 
                                            data=self._checklist_data)

        self.assertEqual(response.status_code, 200)
    
    def test_delete_checklist(self):
        response = self.client.get(reverse("checklists:delete_checklist",
                                            kwargs={"pk": "Test Checklist"}))
        self.assertEqual(response.status_code, 302)#because the page redirects
        self.create_test_checklist()


class AjaxRequestsTests(TestCase, TestDataMixin):
    @classmethod
    def setUpTestData(cls):
        super(AjaxRequestsTests, cls).setUpTestData()
        cls.create_dummy_accounts()
        cls.create_test_checklist()

    @classmethod
    def setUpClass(cls):
        super(AjaxRequestsTests, cls).setUpClass()
        cls.client = Client()


    def test_add_task(self):
        session = self.client.session
        session["tasks"] = []
        session.save()
        response = self.client.post(reverse("checklists:add_task"), 
                                    {"task":"Some Test Task"},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.content, "0")# '0' indicates success


    def test_remove_task(self):
        #need to learn how to set up a session
        pass
    
    def test_hold_checklist(self):
        response = self.client.post(reverse("checklists:hold_checklist",
                                    kwargs={"pk": "Test Checklist"}), 
                                    {"reason":"Some Test Reason",
                                    "username": "Test User",
                                    "password": "test123"},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)

