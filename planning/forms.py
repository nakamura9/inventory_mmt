import datetime

from django import forms

from inv.models import Machine
from common_base.models import Account
from common_base.forms import BootstrapMixin


class CalenderFilterForm(BootstrapMixin):
    """Base class for date based filter forms

    Fields: machine, resolver, checklists, planned_jobs"""
    machine = forms.ModelChoiceField(Machine.objects.all(), required=False)
    resolver = forms.ModelChoiceField(Account.objects.all(), required=False)
    checklists = forms.BooleanField(initial=True, required=False)
    planned_jobs = forms.BooleanField(initial=True, required=False)
    #orders = forms.BooleanField(initial=True)


class MonthViewFilterForm(CalenderFilterForm):
    """Filters based on year and month"""
    year= forms.ChoiceField(choices = [(i, i)for i in range(2015, 2099)], 
                        initial=datetime.date.today().year,
                        required=False)

    month = forms.ChoiceField(choices = [(i, i) for i in range(1,13)],
                            initial=datetime.date.today().month,
                            required=False)
    


class WeekViewFilterForm(MonthViewFilterForm):
    """Inherits from month view and filters by year, month, week"""

    week = forms.ChoiceField(choices = [(i, i) for i in range(1,6)],
                            initial=datetime.date.today().month,
                            required=False)


class DayViewFilterForm(CalenderFilterForm):
    """Filters by date alone"""

    date = forms.CharField()