from django import forms
from .models import Account

class BootstrapMixin(forms.Form):
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


class userForm(forms.ModelForm, BootstrapMixin):
            
    class Meta:
        model = Account
        fields = ["username", "role","first_name", "last_name", "password"]
