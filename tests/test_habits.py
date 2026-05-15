import pytest
from django.urls import reverse
from django.utils import timezone

from habits.models import Habit, HabitCompletion


@pytest.mark.django_db
def test_habit_list_requires_auth(client):
    response = client.get(reverse("habit_list"))

    assert response.status_code == 302
    assert response.url.startswith(reverse("login"))


@pytest.mark.django_db
def test_create_habit(authenticated_client, user):
    response = authenticated_client.post(
        reverse("habit_create"),
        data={
            "title": "Morning run",
            "description": "Run for 15 minutes",
            "frequency": Habit.FrequencyChoices.DAILY,
            "target_count": 1,
            "color": "#123456",
            "is_active": True,
        },
    )

    created_habit = Habit.objects.get(title="Morning run")

    assert response.status_code == 302
    assert response.url == reverse("habit_detail", kwargs={"pk": created_habit.pk})
    assert created_habit.user == user


@pytest.mark.django_db
def test_update_habit(authenticated_client, habit):
    response = authenticated_client.post(
        reverse("habit_update", kwargs={"pk": habit.pk}),
        data={
            "title": "Updated title",
            "description": "Updated description",
            "frequency": Habit.FrequencyChoices.WEEKLY,
            "target_count": 3,
            "color": "#654321",
            "is_active": True,
        },
    )

    habit.refresh_from_db()

    assert response.status_code == 302
    assert response.url == reverse("habit_detail", kwargs={"pk": habit.pk})
    assert habit.title == "Updated title"
    assert habit.frequency == Habit.FrequencyChoices.WEEKLY
    assert habit.target_count == 3


@pytest.mark.django_db
def test_delete_habit(authenticated_client, habit):
    response = authenticated_client.post(reverse("habit_delete", kwargs={"pk": habit.pk}))

    assert response.status_code == 302
    assert response.url == reverse("habit_list")
    assert not Habit.objects.filter(pk=habit.pk).exists()


@pytest.mark.django_db
def test_user_cannot_access_another_users_habit(client, another_user, habit):
    client.force_login(another_user)

    response = client.get(reverse("habit_detail", kwargs={"pk": habit.pk}))

    assert response.status_code == 404


@pytest.mark.django_db
def test_complete_habit(authenticated_client, habit):
    response = authenticated_client.post(
        reverse("habit_complete", kwargs={"pk": habit.pk}),
        data={"note": "Finished"},
    )

    completion = HabitCompletion.objects.get(habit=habit, completed_at=timezone.localdate())

    assert response.status_code == 302
    assert response.url == reverse("habit_detail", kwargs={"pk": habit.pk})
    assert completion.note == "Finished"


@pytest.mark.django_db
def test_duplicate_completion_for_same_day_is_not_created(authenticated_client, habit, completed_habit):
    response = authenticated_client.post(
        reverse("habit_complete", kwargs={"pk": habit.pk}),
        data={"note": "Second try"},
    )

    completions = HabitCompletion.objects.filter(habit=habit, completed_at=timezone.localdate())

    assert response.status_code == 302
    assert response.url == reverse("habit_detail", kwargs={"pk": habit.pk})
    assert completions.count() == 1
    assert completions.get().note == completed_habit.note
