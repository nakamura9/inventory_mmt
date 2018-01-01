from django import forms
from .models import Account, Category

class BootstrapMixin(forms.Form):
    """This class intergrates bootstrap into select form fields
    
    The class is a mixin that adds the 'form-control class' to each field in the form as well as making each text input have a placeholder instead of a label. It can be used as a common point for inserting other standard behaviour in the future."""

    def __init__(self, *args, **kwargs):
        super(BootstrapMixin, self).__init__(*args, **kwargs)
        for field in self.fields:
            field = self.fields.get(field)
            field.widget.attrs['class'] ="form-control"
            """if isinstance(field.widget, forms.TextInput):
                field.widget.attrs['placeholder'] =field.label
                field.label = """
            

class userForm(forms.ModelForm, BootstrapMixin):
    """Form used for creating new users on a site
    
    Fields: username, first_name, ,last_name, role, password"""

    class Meta:
        model = Account
        fields = ["username", "role","first_name", "last_name", "password"]


class CategoryForm(forms.ModelForm, BootstrapMixin): 
    """Form for creating categories for organizing content in inventory

    Fields: name, created_for, description"""

    class Meta:
        model = Category
        fields = ["created_for", "name", "description"]

class LoginForm(forms.Form):
    username = forms.ChoiceField([(acc.username, acc.username) for acc in Account.objects.all()])
    password = forms.CharField()