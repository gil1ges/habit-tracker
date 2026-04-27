import pytest
from django.urls import reverse

from users.models import CustomUser


PASSWORD = "StrongPass1!"


@pytest.mark.django_db
def test_successful_registration(client):
    response = client.post(
        reverse("register"),
        data={
            "username": "newuser",
            "email": "newuser@example.com",
            "phone": "+79991234567",
            "bio": "Ready to build habits",
            "password1": PASSWORD,
            "password2": PASSWORD,
        },
    )

    assert response.status_code == 302
    assert response.url == reverse("habit_list")
    assert CustomUser.objects.filter(username="newuser").exists()
    assert str(CustomUser.objects.get(username="newuser").pk) == client.session["_auth_user_id"]


@pytest.mark.django_db
def test_registration_validation_error(client):
    response = client.post(
        reverse("register"),
        data={
            "username": "usr",
            "email": "",
            "password1": PASSWORD,
            "password2": PASSWORD,
        },
    )

    assert response.status_code == 200
    assert not CustomUser.objects.filter(username="usr").exists()
    assert "form" in response.context
    assert response.context["form"].errors


@pytest.mark.django_db
def test_successful_login(client, user):
    response = client.post(
        reverse("login"),
        data={"username": user.username, "password": PASSWORD},
    )

    assert response.status_code == 302
    assert response.url == reverse("habit_list")
    assert client.session["_auth_user_id"] == str(user.pk)


@pytest.mark.django_db
def test_logout_redirect(client, user):
    client.force_login(user)

    response = client.post(reverse("logout"))

    assert response.status_code == 302
    assert response.url == reverse("home")
    assert "_auth_user_id" not in client.session


@pytest.mark.django_db
def test_password_change_page_available_for_authenticated_user(authenticated_client):
    response = authenticated_client.get(reverse("password_change"))

    assert response.status_code == 200
