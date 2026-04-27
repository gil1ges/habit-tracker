from django.urls import path

from .views import (
    HabitCreateView,
    HabitDeleteView,
    HabitDetailView,
    HabitListView,
    HabitUpdateView,
    habit_complete,
)

urlpatterns = [
    path("", HabitListView.as_view(), name="habit_list"),
    path("create/", HabitCreateView.as_view(), name="habit_create"),
    path("<int:pk>/", HabitDetailView.as_view(), name="habit_detail"),
    path("<int:pk>/edit/", HabitUpdateView.as_view(), name="habit_update"),
    path("<int:pk>/delete/", HabitDeleteView.as_view(), name="habit_delete"),
    path("<int:pk>/complete/", habit_complete, name="habit_complete"),
]
