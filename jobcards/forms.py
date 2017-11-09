from django import forms
from django.utils import timezone

from common_base.forms import BootstrapMixin
from common_base.models import Account
from inv.models import Machine
from .models import WorkOrder, PreventativeTask


class WorkOrderCreateForm(forms.ModelForm, BootstrapMixin):
    """Class for creating work orders.
    
    Fields: type, machine, section, subunit, subassembly, component, description, execution_date, estimated_labour_time, assigned_to, priority
    """
    
    class Meta:
        model = WorkOrder
        fields = ["type", "machine", "section", "subunit", "subassembly", "component", "description", "execution_date", "estimated_labour_time", "assigned_to", "priority"]

class WorkOrderCompleteForm(forms.ModelForm, BootstrapMixin):
    """Class for completing workorders.

    Fields: resolver_action, actual_labour_time,
            downtime, completion_date, spares_issued, spares_returned
    """

    class Meta:
        model = WorkOrder
        fields = ["resolver_action", "actual_labour_time",
                "downtime", "completion_date", "spares_issued", "spares_returned"]


class PreventativeTaskCreateForm(forms.ModelForm, BootstrapMixin):
    """Class for creating preventative tasks.

    Fields:"""

    class Meta:
        model = PreventativeTask
        fields = [ "machine", "section", "subunit", "subassembly", "component", "scheduled_for","description",  "frequency", "estimated_labour_time", "estimated_downtime","required_spares", "assignments"]# tasks are handled in the POST


class PreventativeTaskCompleteForm(forms.ModelForm, BootstrapMixin):
    """Class for completing preventative tasks.

    Fields:"""

    class Meta:
        model = PreventativeTask
        fields = ["actual_downtime", "completed_date", "feedback",
                "spares_used"]


class WorkOrderListFilterForm(forms.Form):
    """Form for filtering Work orders in the list view.

    Fields: start_date, end_date, resolver, machine,"""

    def __init__(self, *args, **kwargs):
        super(WorkOrderListFilterForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            field = self.fields.get(field)
            field.widget.attrs['class'] ="form-control"
 
 
    start_date = forms.DateField(required = False)
    end_date = forms.DateField(required = False)
    resolver = forms.ChoiceField(choices = [(acc.pk, acc.username) \
                                    for acc in Account.objects.all()],
                                    required = False)
    machine = forms.ChoiceField(choices = [(mach.pk, mach.machine_name) \
                                        for mach in Machine.objects.all()],
                                        required = False)