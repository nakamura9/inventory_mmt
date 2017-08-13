from django import forms
from inv.models import *
from .models import Category, InventoryItem, Order

# research mixins
class BootstrapMixin(forms.Form):
    def __init__(self, *args, **kwargs):
        super(BootstrapMixin, self).__init__(*args, **kwargs)
        for field in self.fields:
            field = self.fields.get(field)
            field.widget.attrs['class'] ="form-control"
            if isinstance(field.widget, forms.TextInput) or \
                isinstance(field.widget, forms.NumberInput):
                field.widget.attrs['placeholder'] =field.label
                field.label = ""


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

class SubUnitForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = SubUnit
        fields = [ "unit_name", "machine", "unique_id"]


class SubAssyForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = SubAssembly
        fields = ["unit_name", "machine","subunit", "unique_id"]
    
class ComponentForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = Component
        fields = ["component_name", "inventory_number",
                "machine", "subunit", "subassembly", "unique_id"]
    