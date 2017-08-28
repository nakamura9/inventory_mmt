from .models import Breakdown, JobCard, PlannedJob
from django import forms
from django.utils import timezone
from common_base.forms import BootstrapMixin
from common_base.models import Account
from inv.models import Machine

class DateInput(forms.DateInput):
    input_type = "text"

class TimeInput(forms.TimeInput):
    input_type = "time"

class DurationInput(forms.Select):
    def __init__(self, *args, **kwargs):
        super(DurationInput, self).__init__(*args, **kwargs)
        self.attrs["class"] = "form-control"
        self.choices = [("00%d" % i, "00%d" % i) for i in range(10, 60, 5)] \
                        + [("0%d00" % i, "0%d00" % i) for i in range(1, 9)] \
                        + [("%d00" % i, "%d00" % i) for i in range(10, 24)]

class PlannedJobForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = PlannedJob
        fields = ["scheduled_for","resolver", "machine","section", "subunit",
            "description",  "estimated_time"]

    def __init__(self, *args, **kwargs):
        super(PlannedJobForm, self).__init__(*args, **kwargs)
        self.fields["estimated_time"].label = "Estimated Time"
        self.fields["estimated_time"].widget = DurationInput()
        self.fields["machine"].widget.attrs["onchange"] = "prepSectionUpdate()"
        self.fields["section"].widget.attrs["onchange"] = "prepSubUnitUpdate()"


class UnplannedJobForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = Breakdown
        fields = ["requested_by", "resolver", "machine","section", "subunit", "description", 
                    "estimated_time"]
 
    def __init__(self, *args, **kwargs):
        super(UnplannedJobForm, self).__init__(*args, **kwargs)
        self.fields["machine"].widget.attrs["onchange"] = "prepSectionUpdate()"
        self.fields["section"].widget.attrs["onchange"] = "prepSubUnitUpdate()"
        self.fields["estimated_time"].widget = DurationInput()


class JobListFilterForm(forms.Form):
    start_date = forms.DateField()
    end_date = forms.DateField()
    resolver = forms.ChoiceField(choices = [(acc.pk, acc.username) \
                                    for acc in Account.objects.all()])
    machine = forms.ChoiceField(choices = [(mach.pk, mach.machine_name) \
                                                for mach in Machine.objects.all()])