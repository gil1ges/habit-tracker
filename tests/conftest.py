import pytest
from django.utils import timezone

from habits.models import Habit, HabitCompletion
from users.models import CustomUser


TEST_PASSWORD = "StrongPass1!"


@pytest.fixture
def user(db) -> CustomUser:
    return CustomUser.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password=TEST_PASSWORD,
        phone="+79991234567",
    )


@pytest.fixture
def another_user(db) -> CustomUser:
    return CustomUser.objects.create_user(
        username="anotheruser",
        email="another@example.com",
        password=TEST_PASSWORD,
        phone="+79876543210",
    )


@pytest.fixture
def authenticated_client(client, user):
    client.force_login(user)
    return client


@pytest.fixture
def habit(user) -> Habit:
    return Habit.objects.create(
        user=user,
        title="Read daily",
        description="Read for 20 minutes",
        frequency=Habit.FrequencyChoices.DAILY,
        target_count=1,
        color="#4CAF50",
        is_active=True,
    )


@pytest.fixture
def completed_habit(habit) -> HabitCompletion:
    return HabitCompletion.objects.create(
        habit=habit,
        completed_at=timezone.localdate(),
        note="Done",
    )
