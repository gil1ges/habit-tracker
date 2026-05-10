from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Habit, HabitCompletion
from .validators import (
    validate_color,
    validate_forbidden_words,
    validate_habit_title,
    validate_target_count,
)


class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = [
            "title",
            "description",
            "frequency",
            "target_count",
            "color",
            "is_active",
        ]
        labels = {
            "title": "Название",
            "description": "Описание",
            "frequency": "Периодичность",
            "target_count": "Целевое количество",
            "color": "Цвет",
            "is_active": "Активна",
        }
        help_texts = {
            "title": "Короткое и понятное название привычки.",
            "description": "Необязательное описание, которое поможет держать фокус.",
            "frequency": "Выберите, как часто вы хотите выполнять привычку.",
            "target_count": "Сколько раз нужно выполнить привычку за выбранный период.",
            "color": "Цвет в шестнадцатеричном формате, например #4CAF50.",
            "is_active": "Неактивные привычки сохраняются в списке, но их можно временно поставить на паузу.",
        }
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Например, Читать 20 минут",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Добавьте описание или подсказку для привычки",
                    "rows": 4,
                }
            ),
            "frequency": forms.Select(attrs={"class": "form-select"}),
            "target_count": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Сколько раз выполнять за период",
                    "min": 1,
                    "max": 30,
                }
            ),
            "color": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "#4CAF50",
                }
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_title(self) -> str:
        title = self.cleaned_data["title"].strip()
        validate_habit_title(title)
        validate_forbidden_words(title)
        return title

    def clean_target_count(self) -> int:
        target_count = self.cleaned_data["target_count"]
        validate_target_count(target_count)
        if target_count > 30:
            raise ValidationError("Целевое количество не может быть больше 30.")
        return target_count

    def clean_color(self) -> str:
        color = self.cleaned_data["color"].strip()
        validate_color(color)
        return color

    def clean_description(self) -> str:
        description = self.cleaned_data.get("description", "").strip()
        if description:
            validate_forbidden_words(description)
        return description

    def clean(self) -> dict:
        cleaned_data = super().clean()
        frequency = cleaned_data.get("frequency")
        target_count = cleaned_data.get("target_count")
        is_active = cleaned_data.get("is_active")
        description = cleaned_data.get("description", "")

        if frequency == Habit.FrequencyChoices.DAILY and target_count and target_count > 7:
            self.add_error(
                "target_count",
                "Для ежедневной привычки целевое количество не может быть больше 7.",
            )

        if is_active is False and not description:
            self.add_error(
                "description",
                "У неактивной привычки должно быть описание.",
            )

        return cleaned_data


class HabitCompletionForm(forms.ModelForm):
    class Meta:
        model = HabitCompletion
        fields = ["completed_at", "note"]
        labels = {
            "completed_at": "Дата выполнения",
            "note": "Заметка",
        }
        help_texts = {
            "completed_at": "Дата фиксируется на сегодня.",
            "note": "Короткий комментарий о том, как прошло выполнение.",
        }
        widgets = {
            "completed_at": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "note": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Короткая заметка о выполнении",
                }
            ),
        }

    def clean_completed_at(self):
        completed_at = self.cleaned_data["completed_at"]
        if completed_at > timezone.localdate():
            raise ValidationError("Нельзя отметить выполнение датой из будущего.")
        return completed_at
