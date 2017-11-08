import datetime

from django.test import TestCase
from django.test import Client
from django.shortcuts import reverse

from checklists import models
from inv import models as inv_models
from common_base.models import Account
from common_base.tests import TestDataMixin

class ModelTests(TestCase, TestDataMixin):
    """"Tests the checklist model creation and the functionality of the properties"""
    
    @classmethod
    def setUpTestData(cls):
        super(ModelTests, cls).setUpTestData()
        cls.create_dummy_accounts()
        cls.create_test_checklist()


    def test_create_checklist(self):
        """creates dummy checklist with data from mixin"""

        self._checklist_data["title"] = "Unit Test Checklist"
        check = models.Checklist.objects.create(**self._checklist_data)
        self.assertIsInstance(check, models.Checklist)


    def test_checklist_properties(self):
        """Checks the 'is_open', 'next' properties"""

        check = models.Checklist.objects.get(title="Test Checklist")
        self.assertTrue(check.is_open)
        check.last_completed_date = datetime.date.today()
        self.assertFalse(check.is_open)
        self.assertEqual(check.next, datetime.date.today() + \
                        datetime.timedelta(days=1))


class TestViews(TestCase, TestDataMixin):
    """Test the get and post requests on the views of the application"""
    
    @classmethod
    def setUpClass(cls):
        super(TestViews, cls).setUpClass()
        cls.client = Client()


    @classmethod
    def setUpTestData(cls):
        super(TestViews, cls).setUpTestData()
        cls.create_dummy_accounts()
        cls.create_test_checklist()

    def test_checklist_detailview(self):
        """Expect status code '200' for get request to checklist_detailview"""
        
        response = self.client.get(reverse("checklists:checklist_details", 
                                    kwargs={"pk": "Test Checklist"}))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["object"].title, "Test Checklist")

    def test_get_checklist_form(self):
        """Expect status code '200' for get request to checklist_form"""

        response = self.client.get(reverse("checklists:create_checklist"))
        self.assertEqual(response.status_code, 200)

    def test_post_checklist_creation_form(self):
        """Expect status code '200' for post request to checklist_creationform
        
        Field data populated by testdatamixin checklist data.
        Session emulated for complete functionality test"""

        session = self.client.session
        session["tasks"] = ["some test task"]
        session.save()
        response = self.client.post(reverse("checklists:create_checklist"),data=self._checklist_data)

        self.assertEqual(response.status_code, 200)
    
    def test_get_checklist_updateview(self):
        """Expect status code '200' for get request to checklist_updateview"""

        response = self.client.get(reverse("checklists:update_checklist",
                                 kwargs={"pk":"Test Checklist"}))
        self.assertEqual(response.status_code, 200)

    def test_post_checklist_updateview(self):
        """Expect status code '200' for post request to checklist_updateview
        
        Field data populated by the testdatamixin checklist data.
        Session emulated for full functionality."""

        session = self.client.session
        session["tasks"] = ["some test task"]
        session.save()
        self._checklist_data["estimated_time"] = "0100"
        response = self.client.post(reverse("checklists:update_checklist",
                                            kwargs={"pk":"Test Checklist"}), 
                                            data=self._checklist_data)

        self.assertEqual(response.status_code, 200)    

    def test_delete_checklist(self):
        """Expect status code '302' for get request to delete_checklist"""
        
        response = self.client.get(reverse("checklists:delete_checklist",
                                            kwargs={"pk": "Test Checklist"}))
        self.assertEqual(response.status_code, 302)#because the page redirects


class AjaxRequestsTests(TestCase, TestDataMixin):
    """Tests requests made via ajax which are associated with checklists"""
    @classmethod
    def setUpTestData(cls):
        super(AjaxRequestsTests, cls).setUpTestData()
        cls.create_dummy_accounts()
        cls.create_test_checklist()

    @classmethod
    def setUpClass(cls):
        super(AjaxRequestsTests, cls).setUpClass()
        cls.client = Client()

    
    def test_hold_checklist(self):
        """Expect status code '200' for get request to hold_checklist"""
        response = self.client.post(reverse("checklists:hold_checklist",
                                    kwargs={"pk": "Test Checklist"}), 
                                    {"reason":"Some Test Reason",
                                    "username": "Test User",
                                    "password": "test123"},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)