from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


class BaseRegisterForm(UserCreationForm):
    phone_number = forms.CharField(
        max_length=13,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter your phone number",
                "autofocus": True,
                "inputmethod": "tel",
            }
        ),
    )

    class Meta:
        model = User
        fields = ["phone_number", "first_name", "last_name", "password1", "password2"]


class SellerRegisterForm(BaseRegisterForm):

    national_id = forms.CharField(max_length=10)

    class Meta(BaseRegisterForm.Meta):
        fields = BaseRegisterForm.Meta.fields + ["natinaol_id"]
        widgets = {
            "bio": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Tell buyers about your business..."}
            )
        }


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=11,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter your phone number",
                "autofocus": True,
                "inputmode": "tel",
            }
        ),
    )
    password = forms.CharField(widget=forms.PasswordInput)
