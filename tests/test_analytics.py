import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_dashboard_requires_auth(client):
    response = client.get(reverse("analytics_dashboard"))

    assert response.status_code == 302
    assert response.url.startswith(reverse("login"))


@pytest.mark.django_db
def test_dashboard_available_for_authenticated_user(authenticated_client, habit, completed_habit, monkeypatch):
    monkeypatch.setattr(
        "analytics.views.get_motivational_quote",
        lambda: {"content": "Keep going", "author": "Tester"},
    )
    monkeypatch.setattr("analytics.views.build_bar_chart", lambda user: "bar")
    monkeypatch.setattr("analytics.views.build_pie_chart", lambda user: "pie")
    monkeypatch.setattr("analytics.views.build_line_chart", lambda user: "line")
    monkeypatch.setattr("analytics.views.build_histogram", lambda user: "histogram")
    monkeypatch.setattr("analytics.views.build_scatter_chart", lambda user: "scatter")

    response = authenticated_client.get(reverse("analytics_dashboard"))

    assert response.status_code == 200
    assert "stats" in response.context
    assert response.context["stats"]["total_habits"] == 1


@pytest.mark.django_db
def test_api_stats_returns_json(authenticated_client, completed_habit):
    response = authenticated_client.get(reverse("analytics_api_stats"))

    assert response.status_code == 200
    assert response["Content-Type"].startswith("application/json")


@pytest.mark.django_db
def test_api_stats_contains_expected_keys(authenticated_client, completed_habit):
    response = authenticated_client.get(reverse("analytics_api_stats"))

    payload = response.json()

    assert set(payload) >= {
        "total_habits",
        "active_habits",
        "total_completions",
        "completed_today",
        "habits",
    }
