import copy
import json
import datetime

from django.test import TestCase, Client
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
        cls.today = datetime.date.today()


    def test_create_checklist(self):
        """creates dummy checklist with data from mixin"""

        self._checklist_data["title"] = "Unit Test Checklist"
        check = models.Checklist.objects.create(**self._checklist_data)
        self.assertIsInstance(check, models.Checklist)


    def test_checklist_is_open(self):
        """Checks the 'is_open' property"""

        check = models.Checklist.objects.get(title="Test Checklist")
        self.assertTrue(check.is_open)
        check.last_completed_date = self.today
        self.assertFalse(check.is_open)

    def test_checklist_next(self):
        """check the next property after a checklist is completed"""
        check = models.Checklist.objects.get(title="Test Checklist")
        check.last_completed_date = self.today
        self.assertEqual(check.next, self.today + \
                        datetime.timedelta(days=1))

    def test_checklist_is_open_on_date(self):
        """checks if checklist is initially open then complete and check if it is now closed"""
        check = models.Checklist.objects.get(title="Test Checklist")
        self.assertTrue(check.is_open_on_date(self.today))
        check.last_completed_date = self.today
        self.assertFalse(check.is_open_on_date(self.today))
        
    def test_checklist_will_be_open_over_period(self):
        """change the frequency, tests if period is acknowledged and then completes the checklist and then checks if the method returns false"""
        check = models.Checklist.objects.get(title="Test Checklist")
        check.frequency = "weekly"
        self.assertTrue(check.will_be_open_over_period(self.today,
            self.today + datetime.timedelta(days=7)))
        check.last_completed_date = self.today
        self.assertFalse(check.will_be_open_over_period(self.today,
            self.today + datetime.timedelta(days=3)))
        
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
                                    kwargs={"pk": models.Checklist.objects.first().pk}))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["object"].title, "Test Checklist")

    def test_get_checklist_form(self):
        """Expect status code '200' for get request to checklist_form"""

        response = self.client.get(reverse("checklists:create_checklist"))
        self.assertEqual(response.status_code, 200)

    def test_post_checklist_creation_form(self):
        """Expect status code '302' for post request to checklist_creationform
        
        Field data populated by testdatamixin checklist data.
        Session emulated for complete functionality test"""
        
        data = copy.deepcopy(self._checklist_data) 
        data["machine"] = data["machine"].pk
        data["resolver"] = data["resolver"].pk
        data["section"] = data["section"].pk
        data["subunit"] = data["subunit"].pk
        data["subassembly"] = ""
        response = self.client.post(reverse("checklists:create_checklist"),data=data)
        self.assertEqual(response.status_code, 302)
    
    def test_get_checklist_updateview(self):
        """Expect status code '200' for get request to checklist_updateview"""

        response = self.client.get(reverse("checklists:update_checklist",
                                 kwargs={"pk":models.Checklist.objects.first().pk}))
        self.assertEqual(response.status_code, 200)

    def test_post_checklist_updateview(self):
        """Expect status code '302' for post request to checklist_updateview
        
        Field data populated by the testdatamixin checklist data.
        Session emulated for full functionality."""
        data = copy.deepcopy(self._checklist_data)
        data["machine"] = data["machine"].pk
        data["resolver"] = data["resolver"].pk
        data["section"] = data["section"].pk
        data["subunit"] = data["subunit"].pk
        data["subassembly"] = ""
        data["estimated_time"] = "0:30:00"
 
        response = self.client.post(reverse("checklists:update_checklist",
                            kwargs={"pk":models.Checklist.objects.first().pk}), 
                                            data=data)

        self.assertEqual(response.status_code, 302)    

    def test_delete_checklist(self):
        """Expect status code '302' for get request to delete_checklist"""
        
        response = self.client.get(reverse("checklists:delete_checklist",
                                            kwargs={"pk": models.Checklist.objects.first().pk}))
        self.assertEqual(response.status_code, 302)#because the page redirects

    def test_get_checklist_complete_view(self):
        """test the completion page """
        response = self.client.get(reverse("checklists:complete_checklist", 
                    kwargs={"pk": models.Checklist.objects.first().pk}))
        self.assertEqual(response.status_code, 200)

    def test_post_checklist_complete_view(self):
        """tests the completion logic"""
        check = models.Checklist.objects.first()
        response = self.client.post(reverse("checklists:complete_checklist",
                    kwargs={"pk": check.pk}),
                    data={"user": check.resolver.username,
                            "password": "test123",
                            "comment": "Some comment"})

        self.assertEqual(response.status_code, 302)
        check = models.Checklist.objects.first()#to refresh 
        self.assertFalse(check.is_open)

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
        check = models.Checklist.objects.first()
        response = self.client.post(reverse("checklists:hold_checklist",
                                    kwargs={"pk": check.pk}), 
                                    {"reason":"Some Test Reason",
                                    "username": check.resolver.username,
                                    "password": "test123"},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        resp_data = json.loads(response.content)
        self.assertTrue(resp_data["authenticated"])#failing to authenticate
    