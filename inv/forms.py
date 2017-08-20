from django import forms
from .models import *
from common_base.forms import BootstrapMixin

class CategoryForm(forms.ModelForm, BootstrapMixin): 
    class Meta:
        model = Category
        fields = ["name", "description"]


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
                "estimated_value", "manufacturer", 
                "unique_id"]

class SectionForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = Section
        fields = [ "section_name", "machine", "unique_id"]


class SubUnitForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = SubUnit
        fields = [ "unit_name", "machine", "section", "unique_id"]


class SubAssyForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = SubAssembly
        fields = ["unit_name", "machine", "section", "subunit", "unique_id"]
    
class ComponentForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = Component
        fields = ["component_name", 
                "machine", "section", "subunit", "subassembly", "unique_id"]
    