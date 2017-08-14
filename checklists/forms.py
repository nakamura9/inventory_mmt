from django import forms
from common_base.forms import BootstrapMixin
from .models import Checklist


class CheckListCreateForm(forms.ModelForm, BootstrapMixin):
    def __init__(self, *args , **kwargs):
        super(CheckListCreateForm, self).__init__(*args, **kwargs)
        self.fields["machine"].widget.attrs["onchange"] = \
                "prepSubUnitUpdate()"
        self.fields["subunit"].widget.attrs["onchange"] = \
                "prepSubAssemblyUpdate()"
        
    class Meta:
        model= Checklist
        fields = ["title", "creation_date", 'estimated_time', 'start_time',
                    "machine", "subunit", "subassembly", "resolver", 
                    "category", "frequency"]
