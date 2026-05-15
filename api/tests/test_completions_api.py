from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from habits.models import Habit, HabitCompletion

User = get_user_model()
TEST_PASSWORD = "StrongPass1!"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="completionuser",
        email="completionuser@example.com",
        password=TEST_PASSWORD,
    )


@pytest.fixture
def another_user(db):
    return User.objects.create_user(
        username="othercompletionuser",
        email="othercompletionuser@example.com",
        password=TEST_PASSWORD,
    )


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def habit(user):
    return Habit.objects.create(
        user=user,
        title="Read daily",
        description="Read for 20 minutes",
        frequency=Habit.FrequencyChoices.DAILY,
        target_count=1,
        color="#4CAF50",
        is_active=True,
    )


@pytest.mark.django_db
def test_create_completion(authenticated_client, habit):
    today = timezone.localdate()

    response = authenticated_client.post(
        reverse("api-completions-list"),
        data={"habit": habit.pk, "completed_at": today.isoformat(), "note": "Done"},
        format="json",
    )

    completion = HabitCompletion.objects.get(habit=habit, completed_at=today)

    assert response.status_code == 201
    assert completion.note == "Done"


@pytest.mark.django_db
def test_cannot_create_completion_for_another_users_habit(
    authenticated_client,
    another_user,
):
    other_habit = Habit.objects.create(
        user=another_user,
        title="Other habit",
        description="Hidden",
    )

    response = authenticated_client.post(
        reverse("api-completions-list"),
        data={"habit": other_habit.pk, "completed_at": timezone.localdate().isoformat()},
        format="json",
    )

    assert response.status_code == 400
    assert not HabitCompletion.objects.filter(habit=other_habit).exists()


@pytest.mark.django_db
def test_cannot_create_future_completion(authenticated_client, habit):
    future_date = timezone.localdate() + timedelta(days=1)

    response = authenticated_client.post(
        reverse("api-completions-list"),
        data={"habit": habit.pk, "completed_at": future_date.isoformat()},
        format="json",
    )

    assert response.status_code == 400
    assert not HabitCompletion.objects.filter(habit=habit).exists()


@pytest.mark.django_db
def test_duplicate_completion_is_rejected(authenticated_client, habit):
    today = timezone.localdate()
    HabitCompletion.objects.create(habit=habit, completed_at=today, note="First")

    response = authenticated_client.post(
        reverse("api-completions-list"),
        data={"habit": habit.pk, "completed_at": today.isoformat(), "note": "Second"},
        format="json",
    )

    assert response.status_code == 400
    assert HabitCompletion.objects.filter(habit=habit, completed_at=today).count() == 1


@pytest.mark.django_db
def test_complete_action_creates_todays_completion(authenticated_client, habit):
    response = authenticated_client.post(
        reverse("api-habits-complete", kwargs={"pk": habit.pk}),
        data={"note": "Finished"},
        format="json",
    )

    completion = HabitCompletion.objects.get(
        habit=habit,
        completed_at=timezone.localdate(),
    )

    assert response.status_code == 201
    assert completion.note == "Finished"


@pytest.mark.django_db
def test_repeated_complete_does_not_duplicate_completion(authenticated_client, habit):
    complete_url = reverse("api-habits-complete", kwargs={"pk": habit.pk})

    first_response = authenticated_client.post(complete_url, format="json")
    second_response = authenticated_client.post(complete_url, format="json")

    assert first_response.status_code == 201
    assert second_response.status_code == 200
    assert HabitCompletion.objects.filter(
        habit=habit,
        completed_at=timezone.localdate(),
    ).count() == 1


@pytest.mark.django_db
def test_habit_completions_returns_only_completions_for_this_habit(
    authenticated_client,
    user,
    habit,
):
    today = timezone.localdate()
    other_habit = Habit.objects.create(
        user=user,
        title="Stretch",
        description="Stretch for 5 minutes",
    )
    own_completion = HabitCompletion.objects.create(
        habit=habit,
        completed_at=today,
        note="Done",
    )
    other_completion = HabitCompletion.objects.create(
        habit=other_habit,
        completed_at=today,
        note="Not in this list",
    )

    response = authenticated_client.get(
        reverse("api-habits-completions", kwargs={"pk": habit.pk}),
    )
    payload = response.json()
    completion_ids = {item["id"] for item in payload}

    assert response.status_code == 200
    assert own_completion.id in completion_ids
    assert other_completion.id not in completion_ids
