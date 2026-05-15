import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_schema_available(api_client):
    response = api_client.get(reverse("api-schema"))

    assert response.status_code == 200


@pytest.mark.django_db
def test_docs_available(api_client):
    response = api_client.get(reverse("api-docs"))

    assert response.status_code == 200
