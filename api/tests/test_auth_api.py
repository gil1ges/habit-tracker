import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

User = get_user_model()
TEST_PASSWORD = "StrongPass1!"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="apiuser",
        email="apiuser@example.com",
        password=TEST_PASSWORD,
        phone="+79991234567",
    )


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.mark.django_db
def test_register_success(api_client):
    response = api_client.post(
        reverse("api-register"),
        data={
            "username": "newuser",
            "email": "newuser@example.com",
            "phone": "+79990000000",
            "password": TEST_PASSWORD,
            "password2": TEST_PASSWORD,
        },
        format="json",
    )

    created_user = User.objects.get(username="newuser")

    assert response.status_code == 201
    assert response.json()["id"] == created_user.id
    assert created_user.email == "newuser@example.com"
    assert created_user.check_password(TEST_PASSWORD)


@pytest.mark.django_db
def test_register_password_mismatch(api_client):
    response = api_client.post(
        reverse("api-register"),
        data={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": TEST_PASSWORD,
            "password2": "AnotherStrongPass1!",
        },
        format="json",
    )

    assert response.status_code == 400
    assert not User.objects.filter(username="newuser").exists()


@pytest.mark.django_db
def test_token_obtain_success(api_client, user):
    response = api_client.post(
        reverse("api-token-obtain"),
        data={"username": user.username, "password": TEST_PASSWORD},
        format="json",
    )

    payload = response.json()

    assert response.status_code == 200
    assert "access" in payload
    assert "refresh" in payload


@pytest.mark.django_db
def test_users_me_requires_auth(api_client):
    response = api_client.get(reverse("api-users-me"))

    assert response.status_code in (401, 403)


@pytest.mark.django_db
def test_users_me_returns_current_user(authenticated_client, user):
    response = authenticated_client.get(reverse("api-users-me"))

    payload = response.json()

    assert response.status_code == 200
    assert payload["id"] == user.id
    assert payload["username"] == user.username
    assert payload["email"] == user.email


@pytest.mark.django_db
def test_users_me_patch_updates_bio_phone(authenticated_client, user):
    response = authenticated_client.patch(
        reverse("api-users-me"),
        data={"bio": "Building better habits.", "phone": "+70000000000"},
        format="json",
    )

    user.refresh_from_db()

    assert response.status_code == 200
    assert user.bio == "Building better habits."
    assert user.phone == "+70000000000"
