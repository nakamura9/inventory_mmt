from django import forms
from common_base.models import Account
from inv.models import Machine
from common_base.forms import BootstrapMixin

class PlannedMaintenanceFilterForm(forms.Form):
        checklists = forms.BooleanField()
        planned_jobs = forms.BooleanField()
        resolver = forms.ChoiceField(choices = [(acc.pk, acc.username) \
                                    for acc in Account.objects.all()])
        machine = forms.ChoiceField(choices = [(mach.pk, mach.machine_name) \
                                                for mach in Machine.objects.all()])
        start_date = forms.DateField()
        end_date = forms.DateField()
