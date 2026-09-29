from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Address, SellerProfile, User


class BaseRegisterForm(UserCreationForm):
    phone_number = forms.CharField(
        max_length=13,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter your phone number",
                "autofocus": True,
                "inputmode": "tel",
                "class": "form-control",
            }
        ),
    )
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "First name"}
        )
    )
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Last name"}
        )
    )

    class Meta:
        model = User
        fields = ["phone_number", "first_name", "last_name", "password1", "password2"]
        widgets = {
            "password1": forms.PasswordInput(attrs={"class": "form-control"}),
            "password2": forms.PasswordInput(attrs={"class": "form-control"}),
        }


class SellerRegisterForm(BaseRegisterForm):

    national_id = forms.CharField(
        max_length=10,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "National ID"}
        ),
    )

    class Meta(BaseRegisterForm.Meta):
        fields = BaseRegisterForm.Meta.fields + ["national_id"]
        widgets = {
            **BaseRegisterForm.Meta.widgets,
            "bio": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Tell buyers about your business...",
                    "class": "form-control",
                }
            ),
        }


class EditSellerProfileForm(forms.ModelForm):
    address = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Your shop or business address",
            }
        ),
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Tell customers about your business...",
            }
        ),
    )

    class Meta:
        model = SellerProfile
        fields = ["address", "bio"]


class BecomeSellerForm(EditSellerProfileForm):
    national_id = forms.CharField(
        max_length=10,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "National ID",
            }
        ),
    )

    class Meta(EditSellerProfileForm.Meta):
        fields = ["national_id"] + EditSellerProfileForm.Meta.fields


class AddressForm(forms.ModelForm):
    phone_field_name = "receiver_phone"

    class Meta:
        model = Address
        fields = [
            "receiver_name",
            "receiver_phone",
            "province",
            "city",
            "address_line",
            "postal_code",
            "is_default",
        ]
        widgets = {
            "receiver_name": forms.TextInput(attrs={"class": "form-control"}),
            "receiver_phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter phone number",
                    "inputmode": "tel",
                }
            ),
            "province": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "address_line": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "postal_code": forms.TextInput(attrs={"class": "form-control"}),
            "is_default": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=13,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter your phone number",
                "autofocus": True,
                "inputmode": "tel",
                "class": "form-control",
            }
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        )
    )
