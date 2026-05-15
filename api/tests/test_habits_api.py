import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from habits.models import Habit

User = get_user_model()
TEST_PASSWORD = "StrongPass1!"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="habituser",
        email="habituser@example.com",
        password=TEST_PASSWORD,
    )


@pytest.fixture
def another_user(db):
    return User.objects.create_user(
        username="otherhabituser",
        email="otherhabituser@example.com",
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


def _habit_payload(**overrides):
    payload = {
        "title": "Morning run",
        "description": "Run for 15 minutes",
        "frequency": Habit.FrequencyChoices.DAILY,
        "target_count": 1,
        "color": "#123456",
        "is_active": True,
    }
    payload.update(overrides)
    return payload


@pytest.mark.django_db
def test_habits_list_requires_auth(api_client):
    response = api_client.get(reverse("api-habits-list"))

    assert response.status_code in (401, 403)


@pytest.mark.django_db
def test_authenticated_user_sees_only_own_habits(
    authenticated_client,
    user,
    another_user,
):
    own_habit = Habit.objects.create(
        user=user,
        title="Own habit",
        description="Visible",
    )
    other_habit = Habit.objects.create(
        user=another_user,
        title="Other habit",
        description="Hidden",
    )

    response = authenticated_client.get(reverse("api-habits-list"))
    payload = response.json()
    habit_ids = {item["id"] for item in payload}

    assert response.status_code == 200
    assert own_habit.id in habit_ids
    assert other_habit.id not in habit_ids


@pytest.mark.django_db
def test_create_habit(authenticated_client, user):
    response = authenticated_client.post(
        reverse("api-habits-list"),
        data=_habit_payload(),
        format="json",
    )

    created_habit = Habit.objects.get(title="Morning run")

    assert response.status_code == 201
    assert created_habit.user == user
    assert created_habit.color == "#123456"


@pytest.mark.django_db
def test_retrieve_habit(authenticated_client, habit):
    response = authenticated_client.get(
        reverse("api-habits-detail", kwargs={"pk": habit.pk}),
    )

    payload = response.json()

    assert response.status_code == 200
    assert payload["id"] == habit.id
    assert payload["title"] == habit.title
    assert payload["completion_count"] == 0
    assert payload["last_completed"] is None


@pytest.mark.django_db
def test_update_habit(authenticated_client, habit):
    response = authenticated_client.patch(
        reverse("api-habits-detail", kwargs={"pk": habit.pk}),
        data={"title": "Updated habit", "target_count": 2, "color": "#654321"},
        format="json",
    )

    habit.refresh_from_db()

    assert response.status_code == 200
    assert habit.title == "Updated habit"
    assert habit.target_count == 2
    assert habit.color == "#654321"


@pytest.mark.django_db
def test_delete_habit(authenticated_client, habit):
    response = authenticated_client.delete(
        reverse("api-habits-detail", kwargs={"pk": habit.pk}),
    )

    assert response.status_code == 204
    assert not Habit.objects.filter(pk=habit.pk).exists()


@pytest.mark.django_db
def test_cannot_access_another_users_habit(
    authenticated_client,
    another_user,
):
    other_habit = Habit.objects.create(
        user=another_user,
        title="Other habit",
        description="Hidden",
    )

    response = authenticated_client.get(
        reverse("api-habits-detail", kwargs={"pk": other_habit.pk}),
    )

    assert response.status_code == 404
