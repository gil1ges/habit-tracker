"""URL configuration for the Habit Tracker project."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("django.contrib.auth.urls")),
    path("habits/", include("habits.urls")),
    path("analytics/", include("analytics.urls")),
]
