from django import forms
from common_base.models import Account, Category
from inv.models import Machine, Spares
from .models import Report
from common_base.forms import BootstrapMixin
from django.utils.html import mark_safe

class SearchWidget(forms.widgets.TextInput):
    def __init__(self, model, *args, **kwargs):
        super(SearchWidget, self).__init__(*args, **kwargs)
        self.model = model
        

    def render(self, name, value, attrs=None):
        if self.attrs:
            self.attrs["list"] = name + "_datalist"

        container = """<div class="input-group">
    %s
    <span class="input-group-btn">
        <button onclick="addItem()" type="button" class="btn btn-default"><span class="glyphicon glyphicon-plus" aria-hidden="true" ></span></button>
    </span>
    <datalist id="%s_datalist"></datalist>
</div>"""
        html = super(SearchWidget, self).render(name, value, attrs)
        script = """<script type="text/javascript">
        $("#{0}").keyup(function(){{
            if($("#{0}").val().length > 2){{
                updateDatalist("{0}", "{1}", "{2}");
            }}
        }});
            </script>""".format("id_"+name, self.model, name+"_datalist")
        container = container % (html, name)
        container += script 

        return mark_safe(container)

class FormWizardOne(forms.Form):
    def __init__(self, *args, **kwargs):
        super(FormWizardOne, self).__init__(*args, **kwargs)
        for field in self.fields:
            field = self.fields.get(field)
            field.widget.attrs['class'] ="form-control"

    author = forms.ModelChoiceField(Account.objects.all())
    target = forms.ModelChoiceField(Account.objects.all())
    start_period = forms.DateField()
    end_period = forms.DateField()
    category = forms.ModelChoiceField(Category.objects.filter(created_for="reports"))
    

class MaintenanceReportForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(MaintenanceReportForm, self).__init__(*args, **kwargs)
        #self.fields["level"].widget.attrs["onchange"] = "selectModel()"
        for field in self.fields:
            field = self.fields.get(field)
            field.widget.attrs['class'] ="form-control"
        
        self.fields["section"].widget.attrs["onchange"] = "prepSubUnitUpdate()"
        self.fields["subunit"].widget.attrs["onchange"] = "prepSubAssemblyUpdate()"
        self.fields["subassembly"].widget.attrs["onchange"] = "prepComponentUpdate()"
        self.fields["machine"].widget.attrs["onchange"] = "prepSectionUpdate()"


    scope = forms.ChoiceField(choices =[("maintenance_plan",
                                             "Maintenance Plan"),
                                        ("component_failure",
                                            "Component Failure"),
                                        ("machine_availability",
                                            "Machine Availability"),
                                        ("breakdown_report", "Breakdown Report")])
    """level = forms.ChoiceField(choices=[("machine", "Level 1: Machine"),
                                        ("section", "Level 2: Section"),
                                        ("subunit", "Level 3: Sub-Unit"),
                                        ("subassembly", "Level 4: Sub-Assembly"),
                                        ("component", "Level 5: Component")])
    equipment = forms.CharField(widget = SearchWidget("component"))"""
    machine = forms.ModelChoiceField(Machine.objects.all())
    section = forms.ChoiceField(required=False)
    subunit = forms.ChoiceField(required=False)
    subassembly = forms.ChoiceField(required=False)
    component = forms.ChoiceField(required=False)




class InventoryReportForm(forms.Form):
    def __init__(self, *args, **kwargs):

        super(InventoryReportForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            field = self.fields.get(field)
            field.widget.attrs['class'] ="form-control"
    
    def clean(self):
        spares_chosen = self.data.getlist("spares_chosen", None)
        if spares_chosen:
            self.cleaned_data["spares_chosen"] = spares_chosen

    scope = forms.ChoiceField(choices=[("spares_used",
                                         "Spares Issuance Report"),
                                        ("spares_required", "Spares Requirements")])
    spares = forms.CharField(widget= SearchWidget("spares"), required=False)
    spares_chosen=forms.CharField(widget=forms.MultipleHiddenInput(), required=False)
    spares_category = forms.ModelChoiceField(Category.objects.filter(created_for="spares"))

