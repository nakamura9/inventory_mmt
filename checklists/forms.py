from django import forms

from common_base.forms import BootstrapMixin
from .models import Checklist
from common_base.models import Account


class CheckListCreateForm(forms.ModelForm, BootstrapMixin):
    """Form for creating checklists.
    
    fields: title, creation_date, estimated_time, start_time,
            machine, section,subunit, subassembly, resolver, 
            category, "frequency"""

    def __init__(self, *args , **kwargs):
        super(CheckListCreateForm, self).__init__(*args, **kwargs)
        self.fields["section"].widget.choices= [('', '--------')]
        self.fields["subunit"].widget.choices= [('', '--------')]
        self.fields["subassembly"].widget.choices= [('', '--------')]
        self.fields["component"].widget.choices= [('', '--------')]
        self.fields["machine"].widget.attrs["onchange"] = \
            "prepSectionUpdate()"
        self.fields["section"].widget.attrs["onchange"] = \
            "prepSubUnitUpdate()"
        self.fields["subunit"].widget.attrs["onchange"] = \
                "prepSubAssemblyUpdate()"
        self.fields["subassembly"].widget.attrs["onchange"] = \
                "prepComponentUpdate()"
        

    class Meta:
        model= Checklist
        fields = ["title", "creation_date", 'estimated_time', 'start_time',
                    "machine", "section","subunit", "subassembly", "component","resolver", 
                    "category", "frequency"]


class ChecklistUpdateForm(forms.ModelForm, BootstrapMixin):
    def __init__(self, *args , **kwargs):
        super(ChecklistUpdateForm, self).__init__(*args, **kwargs)
        
        check = kwargs["instance"]
        
        if check.section:
            self.fields["section"].widget.choices= [(check.section.pk, check.section)]
        
        if check.subunit:
            self.fields["subunit"].widget.choices= [(check.subunit.pk, check.subunit)]
        
        if check.subassembly:
            self.fields["subassembly"].widget.choices= [(check.subassembly.pk, check.subassembly)]
        
    class Meta:
        model= Checklist
        fields = ["title", "creation_date", 'estimated_time', 'start_time',
                    "machine", "section","subunit", "subassembly", "resolver", 
                    "category", "frequency"]