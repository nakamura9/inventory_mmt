from __future__ import unicode_literals
import operator
from itertools import chain

from django.db import models
from django.db.models import Q

from common_base.utilities import filter_by_dates
from jobcards.models import PreventativeTask, WorkOrder
from checklists.models import Checklist


class Report(models.Model):
    created = models.DateField(auto_now=True)
    author = models.ForeignKey("common_base.Account", related_name="%(class)s_author")
    target = models.ManyToManyField("common_base.Account", related_name="%(class)s_target")#dont change
    start_period = models.DateField()
    end_period = models.DateField()
    scope = models.CharField(max_length=32)
    machine = models.ManyToManyField("inv.Machine")
    section = models.ManyToManyField("inv.Section")
    subunit = models.ManyToManyField("inv.SubUnit")
    subassembly = models.ManyToManyField("inv.SubAssembly")
    component = models.ManyToManyField("inv.Component")
    spares = models.ManyToManyField("inv.Spares")
    spares_category = models.ManyToManyField("common_base.Category", related_name="%(class)s_spares_category")
    comments = models.ManyToManyField("common_base.Comment")

    def list_jobs(self):
        """applies numerous filters to the data to match the requirements of the report

        The data is first filtered by dates 
        then its filtered by the equipment supplied to the report
        
        Input
        ------
            None

        Output 
        ------

        3 element tuple of preventative tasks, work_orders and checklists"""

        return self.list_p_tasks(), self.list_work_orders(), self.list_checks()

    def get_q_filters(self):
        q_objs = []

        if self.machine.count() >0:
            q_objs += [Q(machine=mech) for mech in self.machine.all()]

        if self.component.count() >0:
            q_objs += [Q(component=c) for c in self.component.all()]

        if self.subunit.count() >0:
            q_objs += [Q(subunit=s) for s in self.subunit.all()]
        
        if self.subassembly.count() >0:
            q_objs += [Q(subassembly=sa) for sa in self.subassembly.all()]
        
        if self.section.count() >0:
            q_objs += [Q(section=s) for s in self.section.all()]

        return q_objs

    @property
    def equipment_list(self):
        equipment = []
        for cls_ in [self.machine, self.component, self.subassembly, self.subunit, self.section]:
            for e in cls_.all():
                equipment.append(e)

        return equipment


    def add_equipment(self, e):
        """Add an abitrary equipment item to the report based on the length of its pk"""
        mapping = {2:self.machine,
                    4:self.section,
                    6:self.subunit,
                    8:self.subassembly,
                    10:self.component}
        
        mapping[len(e.pk)].add(e)


    def list_checks(self):
        checks = filter_by_dates(Checklist.objects.all(), 
                                self.start_period.strftime("%m/%d/%Y"),
                                    self.end_period.strftime("%m/%d/%Y"))
        q_objs = self.get_q_filters()

        if len(q_objs) > 0:
            return checks.filter(reduce(operator.or_, q_objs))
        else: return checks

    def list_p_tasks(self):
        p_tasks = filter_by_dates(PreventativeTask.objects.all(),
                                    self.start_period.strftime("%m/%d/%Y"),
                                    self.end_period.strftime("%m/%d/%Y"))
        
        q_objs = self.get_q_filters()
        
        if len(q_objs) > 0:
            return p_tasks.filter(reduce(operator.or_, q_objs))
        else: return p_tasks

    def list_work_orders(self):
        wos = filter_by_dates(WorkOrder.objects.all(), 
                        self.start_period.strftime("%m/%d/%Y"),
                        self.end_period.strftime("%m/%d/%Y"))

        
        q_objs = self.get_q_filters()
        
        if len(q_objs) > 0:
            return wos.filter(reduce(operator.or_, q_objs))
        else: return wos