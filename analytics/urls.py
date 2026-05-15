from django.urls import path

from .views import api_stats, dashboard

urlpatterns = [
    path("", dashboard, name="analytics_dashboard"),
    path("api/stats/", api_stats, name="analytics_api_stats"),
]

