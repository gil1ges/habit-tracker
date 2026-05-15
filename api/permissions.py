from rest_framework import permissions

from habits.models import Habit, HabitCompletion


class IsOwner(permissions.BasePermission):
    message = "You do not have permission to access this object."

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Habit):
            return obj.user_id == request.user.id

        if isinstance(obj, HabitCompletion):
            return obj.habit.user_id == request.user.id

        user = getattr(obj, "user", None)
        return user == request.user
