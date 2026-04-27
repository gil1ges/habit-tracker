from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Habit(models.Model):
    class FrequencyChoices(models.TextChoices):
        DAILY = "daily", "Ежедневно"
        WEEKLY = "weekly", "Еженедельно"
        MONTHLY = "monthly", "Ежемесячно"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="habits",
    )
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    frequency = models.CharField(
        max_length=20,
        choices=FrequencyChoices.choices,
        default=FrequencyChoices.DAILY,
    )
    target_count = models.PositiveIntegerField(default=1)
    color = models.CharField(max_length=7, default="#4CAF50")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("habit_detail", kwargs={"pk": self.pk})


class HabitCompletion(models.Model):
    habit = models.ForeignKey(
        Habit,
        on_delete=models.CASCADE,
        related_name="completions",
    )
    completed_at = models.DateField(default=timezone.localdate)
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["habit", "completed_at"]
        ordering = ["-completed_at"]

    def __str__(self) -> str:
        return f"{self.habit.title} - {self.completed_at}"
