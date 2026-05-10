from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

from .validators import (
    validate_color,
    validate_forbidden_words,
    validate_habit_title,
    validate_target_count,
)


class Habit(models.Model):
    class FrequencyChoices(models.TextChoices):
        DAILY = "daily", "Ежедневно"
        WEEKLY = "weekly", "Еженедельно"
        MONTHLY = "monthly", "Ежемесячно"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="habits",
        verbose_name="Пользователь",
    )
    title = models.CharField(
        max_length=100,
        validators=[validate_habit_title, validate_forbidden_words],
        verbose_name="Название",
    )
    description = models.TextField(
        blank=True,
        validators=[validate_forbidden_words],
        verbose_name="Описание",
    )
    frequency = models.CharField(
        max_length=20,
        choices=FrequencyChoices.choices,
        default=FrequencyChoices.DAILY,
        verbose_name="Периодичность",
    )
    target_count = models.PositiveIntegerField(
        default=1,
        validators=[validate_target_count],
        verbose_name="Целевое количество",
    )
    color = models.CharField(
        max_length=7,
        default="#4CAF50",
        validators=[validate_color],
        verbose_name="Цвет",
    )
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлена")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("habit_detail", kwargs={"pk": self.pk})


class HabitCompletion(models.Model):
    habit = models.ForeignKey(
        Habit,
        on_delete=models.CASCADE,
        related_name="completions",
        verbose_name="Привычка",
    )
    completed_at = models.DateField(
        default=timezone.localdate,
        verbose_name="Дата выполнения",
    )
    note = models.CharField(max_length=255, blank=True, verbose_name="Заметка")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        unique_together = ["habit", "completed_at"]
        ordering = ["-completed_at"]
        verbose_name = "Выполнение привычки"
        verbose_name_plural = "Выполнения привычек"

    def __str__(self) -> str:
        return f"{self.habit.title} - {self.completed_at}"
