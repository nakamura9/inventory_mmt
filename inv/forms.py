from django import forms
from inv.models import Account

class BootstrapMixin(object):
    def __init__(self, *args, **kwargs):
        super(BootstrapMixin, self).__init__(*args, **kwargs)
        for field in self.fields:
            field = self.fields.get(field)
            field.widget.attrs['class'] ="form-control"
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs['placeholder'] =field.label
                field.label = ""
            else:
                field.widget.attrs["class"] = "form-control"  


class userForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            field = self.fields.get(field)
            field.widget.attrs['class'] ="form-control"
            field.widget.attrs["placeholder"] = field.label
            field.label =""
            
    class Meta:
        model = Account
        fields = ["username", "first_name", "last_name", "password"]
