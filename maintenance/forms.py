from django import forms
from common_base.models import Account
from inv.models import Machine
from common_base.forms import BootstrapMixin

class PlannedMaintenanceFilterForm(forms.Form):
        def __init__(self, *args, **kwargs):
                super(PlannedMaintenanceFilterForm, self).__init__(*args, **kwargs)
                for field in self.fields:
                        field = self.fields.get(field)
                        field.widget.attrs['class'] ="form-control"


        checklists = forms.BooleanField(required=False)
        planned_jobs = forms.BooleanField(required=False)
        """resolver = forms.ChoiceField(choices = [(acc.pk, acc.username) \
                                    for acc in Account.objects.all()],
                                    required=False)
        machine = forms.ChoiceField(choices = [(mach.pk, mach.machine_name) \
                                                for mach in Machine.objects.all()],
                                                required=False)"""
        start_date = forms.DateField(required=False)
        end_date = forms.DateField(required=False)
