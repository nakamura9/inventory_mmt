from django import forms
import datetime
from inv.models import Machine
from common_base.models import Account
from common_base.forms import BootstrapMixin

class CalenderFilterForm(BootstrapMixin):
    """machine = forms.ChoiceField(choices= [(mech.pk, mech.machine_name) \
                                            for mech in Machine.objects.all()],
                                            required=False)
    resolver = forms.ChoiceField(choices= [(r.pk, r.username) \
                                            for r in Account.objects.all()],
                                            required=False)"""
    checklists = forms.BooleanField(initial=True, required=False)
    planned_jobs = forms.BooleanField(initial=True, required=False)
    #orders = forms.BooleanField(initial=True)


class MonthViewFilterForm(CalenderFilterForm):
    year= forms.ChoiceField(choices = [(i, i)for i in range(2015, 2099)], 
                        initial=datetime.date.today().year,
                        required=False)

    month = forms.ChoiceField(choices = [(i, i) for i in range(1,13)],
                            initial=datetime.date.today().month,
                            required=False)
    


class WeekViewFilterForm(MonthViewFilterForm):
    week = forms.ChoiceField(choices = [(i, i) for i in range(1,6)],
                            initial=datetime.date.today().month,
                            required=False)


class DayViewFilterForm(CalenderFilterForm):    
    date = forms.CharField()