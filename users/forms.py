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
        labels = {
            "username": "Имя пользователя",
            "email": "Электронная почта",
            "phone": "Телефон",
            "avatar": "Аватар",
            "bio": "О себе",
            "password1": "Пароль",
            "password2": "Подтверждение пароля",
        }
        help_texts = {
            "username": "Минимум 5 символов.",
            "email": "Укажите действующий адрес электронной почты.",
            "phone": "Необязательное поле.",
            "avatar": "Необязательное изображение профиля.",
            "bio": "Пара слов о себе.",
        }
        widgets = {
            "username": forms.TextInput(
                attrs={"placeholder": "Например, ivan_petrov"}
            ),
            "email": forms.EmailInput(
                attrs={"placeholder": "name@example.com"}
            ),
            "phone": forms.TextInput(
                attrs={"placeholder": "+7 999 123-45-67"}
            ),
            "bio": forms.Textarea(
                attrs={
                    "placeholder": "Расскажите немного о себе",
                    "rows": 4,
                }
            ),
        }

    def clean_username(self) -> str:
        username = self.cleaned_data["username"]
        if len(username) < 5:
            raise forms.ValidationError(
                "Имя пользователя должно содержать минимум 5 символов."
            )
        return username

    def clean_email(self) -> str:
        email = self.cleaned_data.get("email")
        if not email:
            raise forms.ValidationError("Укажите адрес электронной почты.")
        return email
