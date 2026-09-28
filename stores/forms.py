from django import forms

from .models import Listing, Store


class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ["name", "description", "logo"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "logo": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ["price", "stock_quantity", "is_active"]
        widgets = {
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "stock_quantity": forms.NumberInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
