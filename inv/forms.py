from django import forms
from .models import *
from common_base.forms import BootstrapMixin


class SparesForm(forms.ModelForm, BootstrapMixin):
    """Form used to create Spares items."""

    class Meta:
        model = Spares
        fields = ["name", "description", "stock_id", "quantity", "reorder_level","reorder_quantity","last_order_price","category"]

        widgets = {
            "description": forms.widgets.Textarea
        }

class SparesFilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(SparesFilterForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            field = self.fields.get(field)
            field.widget.attrs['class'] ="form-control"

    sort_by = forms.ChoiceField(choices=[("last_order_price", "Price - Ascending"),
                                    ("quantity", "Quantity - Ascending"),
                                    ("-last_order_price", "Price - Descending"),
                                    ("-quantity", "Quantity - Descending")])
    show_linked_only = forms.BooleanField(required=False)
    #machine = forms.ChoiceField(choices=[(mach.pk, mach.machine_name) \
    #                                    for mach in Machine.objects.all()],
    #                                    required = False)

class AssetForm(forms.ModelForm, BootstrapMixin):
    """Form used to create asset objects"""

    class Meta:
        model = Asset
        fields = ["asset_unique_id", "spares_list", "category"]


class InventoryItemForm(forms.ModelForm, BootstrapMixin):
    """Form used to create inventory items""" 

    class Meta:
        model = InventoryItem
        fields = ["serial_number", "name", "order_number", 
                    "quantity", "order_date", "category",
                        "supplier", "unit_price", "min_stock_level",
                            "reorder_quantity"]


class OrderForm(forms.ModelForm, BootstrapMixin):
    """Form used to create order items"""

    class Meta:
        model = Order
        fields = ["order_number", "description",     "quantity", "unit_price", 
                    "manufacture_date", "delivery_date", "layers", "liner",
                    "flute_profile", "customer", "delivery_status", "production_status"]


class MachineForm(forms.ModelForm, BootstrapMixin):
    """Form used to create machine objects"""
    def __init__(self, *args, **kwargs):
        super(MachineForm, self).__init__(*args, **kwargs)
        self.fields["asset_data"].required = False
        
    class Meta:
        model = Machine
        fields = ["commissioning_date", "machine_name", 
                 "manufacturer", "asset_data",
                "unique_id", "daily_run_hours", "weekly_run_days"]
        

class SectionForm(forms.ModelForm, BootstrapMixin):
    """Form used to create Sections"""

    class Meta:
        model = Section
        fields = [ "section_name", "machine", "unique_id"]


class SubUnitForm(forms.ModelForm, BootstrapMixin):
    """Form used to create SubUnits.
    
    The machine widget has the additional attribute, 'onchange' added during init."""

    class Meta:
        model = SubUnit
        fields = [ "unit_name", "machine", "section", "unique_id"]

    def __init__(self, *args , **kwargs):
        super(SubUnitForm, self).__init__(*args, **kwargs)
        self.fields["machine"].widget.attrs["onchange"] = \
                "prepSectionUpdate()"

class SubAssyForm(forms.ModelForm, BootstrapMixin):
    """Form for creating SubAssemblies.
    
    The machine and section widgets have an 'onchange' attribute added to them during init."""

    class Meta:
        model = SubAssembly
        fields = ["unit_name", "machine", "section", "subunit", "unique_id"]
    
    
    def __init__(self, *args , **kwargs):
        super(SubAssyForm, self).__init__(*args, **kwargs)
        self.fields["machine"].widget.attrs["onchange"] = \
                "prepSectionUpdate()"
        self.fields["section"].widget.attrs["onchange"] = \
                "prepSubUnitUpdate()"


class ComponentForm(forms.ModelForm, BootstrapMixin):
    """Form for creating Components.
    
    The machine, section and subunit widgets have an 'onchange' attribute during init."""
    
    class Meta:
        model = Component
        fields = ["component_name", 
                "machine", "section", "subunit", "subassembly", "unique_id"]
    
    def __init__(self, *args , **kwargs):
        super(ComponentForm, self).__init__(*args, **kwargs)
        self.fields["machine"].widget.attrs["onchange"] = \
                "prepSectionUpdate()"
        self.fields["section"].widget.attrs["onchange"] = \
                "prepSubUnitUpdate()"

        self.fields["subunit"].widget.attrs["onchange"] = \
                "prepSubAssemblyUpdate()"