from django import forms
from django.contrib.auth.forms import UserCreationForm

from users.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            "username",
            "email",
            "phone",
            "avatar",
            "bio",
            "password1",
            "password2",
        )

    def clean_username(self) -> str:
        username = self.cleaned_data["username"]
        if len(username) < 5:
            raise forms.ValidationError("Username must be at least 5 characters long.")
        return username

    def clean_email(self) -> str:
        email = self.cleaned_data.get("email")
        if not email:
            raise forms.ValidationError("Email is required.")
        return email
