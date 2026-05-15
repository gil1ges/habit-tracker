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
        username="statsuser",
        email="statsuser@example.com",
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
    )


@pytest.fixture
def completed_habit(habit):
    return HabitCompletion.objects.create(
        habit=habit,
        completed_at=timezone.localdate(),
        note="Done",
    )


@pytest.mark.django_db
def test_stats_requires_auth(api_client):
    response = api_client.get(reverse("api-stats"))

    assert response.status_code in (401, 403)


@pytest.mark.django_db
def test_stats_returns_json(authenticated_client, completed_habit):
    response = authenticated_client.get(reverse("api-stats"))

    assert response.status_code == 200
    assert response["Content-Type"].startswith("application/json")


@pytest.mark.django_db
def test_stats_contains_expected_keys(authenticated_client, completed_habit):
    response = authenticated_client.get(reverse("api-stats"))

    payload = response.json()

    assert set(payload) >= {
        "total_habits",
        "active_habits",
        "total_completions",
        "completed_today",
        "habits",
    }
