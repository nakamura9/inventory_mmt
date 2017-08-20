from django.test import TestCase, Client
from common_base.tests import TestDataMixin
from django.shortcuts import reverse
from .models import PlannedJob, Breakdown, JobCard
import datetime
from common_base.models import Account
from inv.models import Machine, Section, SubUnit, SubAssembly, Component
from django.utils import timezone


class ViewTests(TestCase, TestDataMixin):
    @classmethod
    def setUpClass(cls):
        super(ViewTests, cls).setUpClass()
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        super(ViewTests, cls).setUpTestData()
        cls.create_dummy_accounts()
        cls.create_test_inventory_models()


    def setUp(self):
        self.common_data = {"description": "Test Description",
                    "creation_epoch": datetime.date.today(),
                    "resolver": Account.objects.first(),
                    "estimated_time": "0030",
                    "completed": False,
                    "machine": Machine.objects.first(),
                    "section": Section.objects.first(),
                    "subunit": SubUnit.objects.first()
                    }
        planned_data = self.common_data
    
        p = PlannedJob(**planned_data)
        p.scheduled_for = timezone.now()
        p.save()

        breakdown_data = self.common_data
        breakdown_data["requested_by"] = Account.objects.first()
        Breakdown(**breakdown_data).save()     
    
    
    def test_get_new_planned_job_view(self):
        response = self.client.get(reverse("jobcards:new_planned_job"))

        self.assertEqual(response.status_code, 200)


    def test_post_new_planned_job_view(self):
        data = self.common_data
        data["description"] = "2"
        data["resolver"] = Account.objects.first().pk
        data["machine"] = Machine.objects.first().pk
        data["subunit"] = SubUnit.objects.first().pk
        data["scheduled_for"] = datetime.date.today()

        response = self.client.post(reverse("jobcards:new_planned_job"),
                                    data = data)


        self.assertIsInstance(PlannedJob.objects.get(description="2"), PlannedJob)


    def test_get_edit_planned_job_view(self):
        response = self.client.get(reverse("jobcards:edit_planned_job",
                                            kwargs={"pk":"1"}))

        self.assertEqual(response.status_code, 200)


    def test_post_edit_planned_job_view(self):
        data = self.common_data
        data["resolver"] = Account.objects.first().pk
        data["machine"] = Machine.objects.first().pk
        data["subunit"] = SubUnit.objects.first().pk
        data["description"] = "Test Edited Description"
        data["scheduled_for"] = datetime.date.today()

        response = self.client.post(reverse("jobcards:edit_planned_job",
                                    kwargs={"pk":PlannedJob.objects.first().pk}), 
                                    data = data)
        
        self.assertEqual(response.status_code, 302)#redirects


    def test_delete_planned_job_view(self):
        response = self.client.get(reverse("jobcards:delete_planned_job",
                                            kwargs={"pk":"1"}))

        self.assertEqual(response.status_code, 302)


    def test_get_new_unplanned_job_view(self):
        response = self.client.get(reverse("jobcards:new_unplanned_job"))

        self.assertEqual(response.status_code, 200)


    def test_post_new_unplanned_job_view(self):
        data = self.common_data
        data["resolver"] = "Test User"
        data["machine"] = Machine.objects.first().pk
        data["scheduled_for"] = datetime.date.today()

        response = self.client.post(reverse("jobcards:new_unplanned_job"),
                                    data = data)

        self.assertEqual(response.status_code, 200)


    def test_get_edit_unplanned_job_view(self):
        response = self.client.get(reverse("jobcards:edit_unplanned_job",
                                            kwargs={"pk": Breakdown.objects.first().pk}))

        self.assertEqual(response.status_code, 200)


    def test_post_edit_unplanned_job_view(self):
        data = self.common_data
        data["resolver"] = Account.objects.first().pk
        data["requested_by"] = Account.objects.first().pk
        data["machine"] = Machine.objects.first().pk
        data["subunit"] = SubUnit.objects.first().pk
        data["scheduled_for"] = datetime.date.today() + datetime.timedelta(days=3)
        data["description"] = "Test Edited Description"

        response = self.client.post(reverse("jobcards:edit_unplanned_job",
                                    kwargs={"pk":Breakdown.objects.first().pk}), 
                                    data = data)

        print response.content
        self.assertEqual(response.status_code, 302)

    def test_delete_unplanned_job_view(self):
        response = self.client.get(reverse("jobcards:delete_unplanned_job",
                                            kwargs={"pk":Breakdown.objects.first().pk}))
        self.assertEqual(response.status_code, 302)

    def test_get_job_list_view(self):
        response = self.client.get(reverse("jobcards:jobs"))

        self.assertEqual(response.status_code, 200)

    def test_get_detailed_planned_job_view(self):
        response = self.client.get(reverse("jobcards:planned_job_detail",
                                            kwargs={"pk":"1"}))

        self.assertEqual(response.status_code, 200)


    def test_post_complete_job_view(self):
        response = self.client.post(reverse("jobcards:complete_job",
                                            args=["1"]), 
                                            data={
                                        "resolver": Account.objects.first().pk,
                                        "resolver_action": "Test resolver action",
                                        "root_cause": "test root cause",
                                        "notes": "test notes...",
                                        "recommended_pm": "Test recommended planned maintenance",
                                        "csrfmiddlewaretoken": "stuff"
                                            })

        self.assertIsInstance(JobCard.objects.get(notes = "test notes..."),
                            JobCard)


    