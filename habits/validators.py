import re

from django.core.exceptions import ValidationError


FORBIDDEN_WORDS = ("bad", "spam", "test123")
HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


def validate_habit_title(value: str) -> None:
    if len(value.strip()) < 3:
        raise ValidationError("Название привычки должно содержать минимум 3 символа.")


def validate_target_count(value: int) -> None:
    if value <= 0 or value > 30:
        raise ValidationError("Целевое количество должно быть от 1 до 30.")


def validate_color(value: str) -> None:
    if not HEX_COLOR_RE.fullmatch(value):
        raise ValidationError("Цвет должен быть в шестнадцатеричном формате: #RRGGBB.")


def validate_forbidden_words(value: str) -> None:
    lowered_value = value.lower()
    if any(word in lowered_value for word in FORBIDDEN_WORDS):
        raise ValidationError("Текст содержит запрещенные слова.")
