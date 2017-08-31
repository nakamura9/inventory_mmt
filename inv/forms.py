from django import forms
from .models import *
from common_base.forms import BootstrapMixin



class InventoryItemForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = InventoryItem
        fields = ["serial_number", "name", "order_number", 
                    "quantity", "order_date", "category",
                        "supplier", "unit_price", "min_stock_level",
                            "reorder_quantity"]


class OrderForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = Order
        fields = ["order_number", "description",     "quantity", "unit_price", 
                    "manufacture_date", "delivery_date", "layers", "liner",
                    "flute_profile", "customer", "delivery_status", "production_status"]


class MachineForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = Machine
        fields = ["commissioning_date", "machine_name", 
                 "manufacturer", 
                "unique_id"]

class SectionForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = Section
        fields = [ "section_name", "machine", "unique_id"]


class SubUnitForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = SubUnit
        fields = [ "unit_name", "machine", "section", "unique_id"]

    def __init__(self, *args , **kwargs):
        super(SubUnitForm, self).__init__(*args, **kwargs)
        self.fields["machine"].widget.attrs["onchange"] = \
                "prepSectionUpdate()"

class SubAssyForm(forms.ModelForm, BootstrapMixin):
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