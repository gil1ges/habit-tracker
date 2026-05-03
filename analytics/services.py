from __future__ import annotations

from datetime import timedelta

from django.db.models import Count, Max
from django.utils import timezone

from habits.models import Habit, HabitCompletion


def get_user_habit_stats(user) -> dict:
    habits_queryset = Habit.objects.filter(user=user).annotate(
        completion_count=Count("completions"),
        last_completed=Max("completions__completed_at"),
    )
    today = timezone.localdate()

    habits = [
        {
            "id": habit.id,
            "title": habit.title,
            "frequency": habit.frequency,
            "target_count": habit.target_count,
            "completion_count": habit.completion_count,
            "last_completed": (
                habit.last_completed.isoformat() if habit.last_completed else None
            ),
        }
        for habit in habits_queryset
    ]

    return {
        "total_habits": habits_queryset.count(),
        "active_habits": habits_queryset.filter(is_active=True).count(),
        "total_completions": HabitCompletion.objects.filter(habit__user=user).count(),
        "completed_today": HabitCompletion.objects.filter(
            habit__user=user,
            completed_at=today,
        ).count(),
        "habits": habits,
    }


def get_completion_by_day(user, days: int = 30) -> list[dict]:
    if days <= 0:
        return []

    end_date = timezone.localdate()
    start_date = end_date - timedelta(days=days - 1)
    completions = (
        HabitCompletion.objects.filter(
            habit__user=user,
            completed_at__range=(start_date, end_date),
        )
        .values("completed_at")
        .annotate(count=Count("id"))
    )
    completion_map = {
        item["completed_at"]: item["count"]
        for item in completions
    }

    return [
        {
            "date": current_date.isoformat(),
            "count": completion_map.get(current_date, 0),
        }
        for current_date in (
            start_date + timedelta(days=offset) for offset in range(days)
        )
    ]


def get_completed_vs_missed(user, days: int = 30) -> dict:
    if days <= 0:
        return {"completed": 0, "missed": 0}

    end_date = timezone.localdate()
    start_date = end_date - timedelta(days=days - 1)
    completed = HabitCompletion.objects.filter(
        habit__user=user,
        completed_at__range=(start_date, end_date),
    ).count()
    active_habits = Habit.objects.filter(user=user, is_active=True).count()
    expected = active_habits * days

    return {
        "completed": completed,
        "missed": max(expected - completed, 0),
    }

