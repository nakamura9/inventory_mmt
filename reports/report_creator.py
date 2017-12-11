import operator

from django.db.models import Q

from jobcards.models import PreventativeTask, WorkOrder
from checklists.models import Checklist
from common_base.utilities import filter_by_dates

def list_jobs(report):
    p_tasks = filter_by_dates(PreventativeTask.objects.all(),
                                report.start_period.strftime("%m/%d/%Y"),
                                report.end_period.strftime("%m/%d/%Y"))
    wos = filter_by_dates(WorkOrder.objects.all(), 
                            report.start_period.strftime("%m/%d/%Y"),
                                report.end_period.strftime("%m/%d/%Y"))
    checks = filter_by_dates(Checklist.objects.all(), 
                            report.start_period.strftime("%m/%d/%Y"),
                                report.end_period.strftime("%m/%d/%Y"))

    q_objs = []
    if report.machine.count() >0:
        q_objs += [Q(machine=mech) for mech in report.machine.all()]

    if report.component.count() >0:
        q_objs += [Q(component=c) for c in report.component.all()]

    if report.subunit.count() >0:
        q_objs += [Q(subunit=s) for s in report.subunit.all()]
    
    if report.subassembly.count() >0:
        q_objs += [Q(subassembly=sa) for sa in report.subassembly.all()]
    
    if report.section.count() >0:
        q_objs += [Q(section=s) for s in report.section.all()]

    if len(q_objs) > 0:
        p_tasks = p_tasks.filter(reduce(operator.or_, q_objs))
        wos = wos.filter(reduce(operator.or_, q_objs))
        checks = checks.filter(reduce(operator.or_, q_objs))

    return p_tasks, wos, checks
    #filter by date
    #filter by equipment
    