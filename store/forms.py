# store/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Product

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'name', 'username', 'role') # Added username here to ensure it's part of the form

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If username is not intended to be filled by user, make it not required or hidden
        # For now, let's make it required as it's in REQUIRED_FIELDS for createsuperuser
        if 'username' in self.fields:
             self.fields['username'].help_text = "Required. Will be auto-populated from email if left blank and not provided."
             # self.fields['username'].required = False # Or set a default/hide

class CustomUserChangeForm(UserChangeForm):
    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = ('email', 'name', 'username', 'role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class AddToBasketForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1, widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'style': 'width: 70px; display: inline-block;'}))
    product_id = forms.IntegerField(widget=forms.HiddenInput())
