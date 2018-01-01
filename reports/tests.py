from django.test import TestCase, Client
import datetime
from django.shortcuts import reverse

from common_base.tests import TestDataMixin
from common_base.models import Account
from inv.models import *
from models import Report
from report_creator import *
from report_plot_creator import *
from jobcards.models import SparesRequest


# Create your tests here.
class ModelTests(TestCase, TestDataMixin):
    @classmethod
    def setUpTestData(cls):
        super(ModelTests, cls).setUpTestData()
        cls.create_dummy_accounts()
        cls.create_test_inventory_models()
        cls.create_test_workorders()
        cls.create_test_checklist()
        cls.create_test_preventative_task()
        Report(author=Account.objects.first(),
            start_period=datetime.date.today() -datetime.timedelta(days=1),
            end_period=datetime.date.today() + datetime.timedelta(days=1),
            scope="maintenance_review").save()
        cls.r = Report.objects.first()
        cls.r.machine.add(Machine.objects.first())
        cls.r.spares.add(Spares.objects.first())

    @classmethod
    def setUpClass(cls):
        super(ModelTests, cls).setUpClass()
        cls.today = datetime.date.today()

    def test_create_report(self):
        r = Report(author=Account.objects.first(),
            start_period=self.today,
            end_period=self.today,
            scope="maintenance_review")
        r.save()
        self.assertEqual(Report.objects.all().count(), 2)

    def test_report_add_equipment(self):
        Machine(unique_id="01", machine_name="01",
            manufacturer="test manufacturer").save()
        self.r.add_equipment(Machine.objects.get(pk="01"))
        self.assertEqual(self.r.machine.count(), 2)

    def test_equipment_list(self):
        Component(unique_id="0101010101",
            component_name="reportcomponent").save()
        self.r.component.add(Component.objects.get(pk="0101010101"))
        self.assertEqual(len(self.r.equipment_list), 2)

    def test_report_get_q_objs(self):
        self.assertEqual(len(self.r.q_objs), 1)

    def test_list_jobs(self):
        jobs =self.r.list_jobs()
        self.assertEqual(len(jobs[0]), 1)
        self.assertEqual(len(jobs[1]), 1)
        self.assertEqual(len(jobs[2]), 1)

class ViewTests(TestCase, TestDataMixin):
    @classmethod
    def setUpTestData(cls):
        super(ViewTests, cls).setUpTestData()
        cls.create_dummy_accounts()
        cls.create_test_inventory_models()
        cls.create_test_workorders()
        cls.create_test_checklist()
        cls.create_test_preventative_task()
        Report(author=Account.objects.first(),
            start_period=datetime.date.today() -datetime.timedelta(days=1),
            end_period=datetime.date.today() + datetime.timedelta(days=1),
            scope="maintenance_review").save()
        cls.r = Report.objects.first()
        cls.r.machine.add(Machine.objects.first())
        cls.r.spares.add(Spares.objects.first())

    @classmethod
    def setUpClass(cls):
        super(ViewTests, cls).setUpClass()
        cls.today = datetime.date.today()
        cls.client = Client()

    def test_home_get(self):
        response = self.client.get(reverse("reports:home"))
        self.assertEqual(response.status_code, 200)

    def test_report_selection_page_get(self):
        response = self.client.get(reverse("reports:report-selection"))
        self.assertEqual(response.status_code, 200)

    def test_report_form_maintenance_review(self):
        response = self.client.get(reverse("reports:report-form",
            kwargs={"type": "maintenance_review"}))
        self.assertEqual(response.status_code, 200)

    def test_report_form_maintenance_plan(self):
        response = self.client.get(reverse("reports:report-form",
            kwargs={"type": "maintenance_plan"}))
        self.assertEqual(response.status_code, 200)

    def test_report_form_breakdown(self):
        response = self.client.get(reverse("reports:report-form",
            kwargs={"type": "breakdown"}))
        self.assertEqual(response.status_code, 200)

    def test_report_form_weak_point(self):
        response = self.client.get(reverse("reports:report-form",
            kwargs={"type": "weak_point"}))
        self.assertEqual(response.status_code, 200)

    def test_report_form_spares_requirements(self):
        response = self.client.get(reverse("reports:report-form",
            kwargs={"type": "spares_requirements"}))
        self.assertEqual(response.status_code, 200)

    def test_report_form_spares_usage(self):
        response = self.client.get(reverse("reports:report-form",
            kwargs={"type": "spares_usage"}))
        self.assertEqual(response.status_code, 200)

    def test_report_form_post_custom(self):
        response = self.client.post(reverse("reports:report-form",
            kwargs={"type": "maintenance_review"}),
            {"author": "Test User",
            "scope": "custom",
            "start": (self.today - \
                datetime.timedelta(days=7)).strftime("%m/%d/%Y"),
            "end": (self.today + \
                datetime.timedelta(days=1)).strftime("%m/%d/%Y")})
        self.assertEqual(response.status_code, 302)

    def test_report_form_post_w_equipment(self):
        Machine(unique_id="01", machine_name="01",
            manufacturer="test manufacturer").save()
        response = self.client.post(reverse("reports:report-form",
            kwargs={"type": "maintenance_review"}),
            {"author": "Test User",
            "scope": "7",
            "equipment[]":"01"})
        self.assertEqual(response.status_code, 302)

    def test_delete_report(self):
        Report(author=Account.objects.first(),
            start_period=self.today,
            end_period=self.today,
            scope="maintenance_review").save()
        response=self.client.get(reverse("reports:delete-report",
            kwargs={"pk":Report.objects.latest("pk").pk}))
        self.assertEqual(response.status_code, 302)

    def test_report_view(self):
        response = self.client.get(reverse("reports:report",
            kwargs={"pk":self.r.pk}))
        self.assertEqual(response.status_code, 200)

    def test_generate_pdf(self):
        response = self.client.get(reverse("reports:generate-pdf",
            kwargs={"pk": self.r.pk}))
        self.assertEqual(response.status_code, 200)

    def test_generate_pdf_with_recycled_context(self):
        self.client.get(reverse("reports:report",
            kwargs={"pk":self.r.pk}))
        response = self.client.get(reverse("reports:generate-pdf",
            kwargs={"pk": self.r.pk}))
        self.assertEqual(response.status_code, 200)


class PlotTests(TestCase, TestDataMixin):
    @classmethod
    def setUpTestData(cls):
        super(PlotTests, cls).setUpTestData()
        cls.create_dummy_accounts()
        cls.create_test_inventory_models()
        cls.create_test_workorders()
        cls.create_test_checklist()
        cls.create_test_preventative_task()
        Report(author=Account.objects.first(),
            start_period=datetime.date.today() -datetime.timedelta(days=1),
            end_period=datetime.date.today() + datetime.timedelta(days=1),
            scope="maintenance_review").save()
        cls.r = Report.objects.first()

    @classmethod
    def setUpClass(cls):
        super(PlotTests, cls).setUpClass()
        cls.today = datetime.date.today()

    #date manipulation methods
    def _switch_dates(self):
        temp = self.r.end_period
        self.r.end_period = self.r.start_period
        self.r.start_period = temp

    def set_forecast(self):
        if self.r.start_period < self.r.end_period:
            self._switch_dates()

    def set_review(self):
        if self.r.start_period > self.r.end_period:
            self._switch_dates()
        
    def set_day_interval(self):
        self.r.start_period = self.today - datetime.timedelta(days=7)

    def set_week_interval(self):
        self.r.start_period = self.today - datetime.timedelta(days=30)

    def set_month_interval(self):
        self.r.start_period = self.today - datetime.timedelta(days=182)

    def test_plot_creator_factory(self):
        pc = PlotCreatorFactory(self.r)
        self.assertIsInstance(pc.create_plotter(),
            MaintenanceReviewPlotFactory)

    def test_weak_point_plot_factory(self):
        self.set_week_interval()
        self.set_review()
        self.create_n_equipment(3)
        for m in Machine.objects.all():
            if len(m.pk) == 2:
                self.r.machine.add(m) 
        self.create_n_work_orders(10, self.r.start_period, self.r.end_period)
        plotter = WeakPointPlotFactory(self.r)
        plotter.generate_plot_urls()
        self.assertTrue(plotter.plot_urls != [])

    def test_breakdown_plot_factory(self):
        self.set_week_interval()
        self.create_n_equipment(3)
        for m in Machine.objects.all():
            if len(m.pk) == 2:
                self.r.machine.add(m) 
        self.create_n_work_orders(10, self.r.start_period, self.r.end_period)
        plotter = BreakdownPlotFactory(self.r)
        plotter.generate_plot_urls()
        self.assertTrue(plotter.plot_urls != [])

    def test_weak_maintenance_plan_factory(self):
        self.set_month_interval()
        self.set_forecast()
        self.create_n_equipment(3)
        for m in Machine.objects.all():
            if len(m.pk) == 2:
                self.r.machine.add(m) 
        self.create_n_preventative_tasks(10, self.r.start_period, self.r.end_period)
        plotter = MaintenancePlanPlotFactory(self.r)
        plotter.generate_plot_urls()
        self.set_review()
        self.assertTrue(plotter.plot_urls != [])
    
class ReportTests(TestCase, TestDataMixin):
    @classmethod
    def setUpTestData(cls):
        super(ReportTests, cls).setUpTestData()
        cls.create_dummy_accounts()
        cls.create_test_inventory_models()
        cls.create_test_workorders()
        cls.create_test_checklist()
        cls.create_test_preventative_task()
        Report(author=Account.objects.first(),
            start_period=datetime.date.today() -datetime.timedelta(days=1),
            end_period=datetime.date.today() + datetime.timedelta(days=1),
            scope="maintenance_review").save()
        cls.r = Report.objects.first()

    @classmethod
    def setUpClass(cls):
        super(ReportTests, cls).setUpClass()
        cls.today = datetime.date.today()

    def test_maintenance_review(self):
        report = MaintenanceReviewReport(self.r)
        report.generate_report()
        self.assertEqual(report.context["total_downtime"], 1)
        #add further assertions

    def test_maintenance_plan(self):
        report = MaintenancePlanReport(self.r)
        report.generate_report()
        self.assertEqual(report.context["p_task_count"], 1)

    def test_weak_point(self):
        report = WeakPointReport(self.r)
        report.generate_report()
        self.assertEqual(report.context["wos"].count(), 1)

    def test_breakdown(self):
        report = BreakdownReport(self.r)
        report.generate_report()
        self.assertEqual(report.context["total_downtime"], 1)

    def test_spares_usage(self):
        WorkOrder.objects.first().spares_issued.add(Spares.objects.first())
        report = SparesUsageReport(self.r)
        report.generate_report()
        self.assertEqual(report.context["spares_count"], 1)

    def test_spares_request(self):
        SparesRequest(name="Some spare",
            unit="ea",
            quantity=1,
            preventative_task=PreventativeTask.objects.first()).save()
        report = SparesRequirementsReport(self.r)
        report.generate_report()
        self.assertEqual(report.context["spares_count"], 1)