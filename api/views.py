import logging

from django.db.models import Count, Max
from django.http import Http404
from django.utils import timezone
from rest_framework import generics
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets

from habits.models import Habit, HabitCompletion

from .permissions import IsOwner
from .serializers import (
    HabitCompletionSerializer,
    HabitSerializer,
    RegisterSerializer,
    UserSerializer,
)

logger = logging.getLogger(__name__)


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        logger.info(
            "API registration succeeded: user_id=%s username=%s",
            user.id,
            user.username,
        )


class MeAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Habit.objects.none()

        return Habit.objects.filter(user=self.request.user).annotate(
            completion_count=Count("completions"),
            last_completed=Max("completions__completed_at"),
        )

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            habit_id = self.kwargs.get(self.lookup_url_kwarg or self.lookup_field)
            habit = Habit.objects.filter(pk=habit_id).select_related("user").first()
            if habit is not None and habit.user_id != self.request.user.id:
                logger.warning(
                    "Unauthorized API habit access attempt: user_id=%s habit_id=%s owner_id=%s",
                    self.request.user.id,
                    habit.pk,
                    habit.user_id,
                )
            raise

    def perform_create(self, serializer):
        habit = serializer.save(user=self.request.user)
        logger.info(
            "API habit created: user_id=%s habit_id=%s title=%s",
            self.request.user.id,
            habit.pk,
            habit.title,
        )

    def perform_update(self, serializer):
        habit = serializer.save()
        logger.info(
            "API habit updated: user_id=%s habit_id=%s title=%s",
            self.request.user.id,
            habit.pk,
            habit.title,
        )

    def perform_destroy(self, instance):
        logger.warning(
            "API habit deleted: user_id=%s habit_id=%s title=%s",
            self.request.user.id,
            instance.pk,
            instance.title,
        )
        instance.delete()

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        habit = self.get_object()
        today = timezone.localdate()
        note = request.data.get("note", "").strip()
        completion, created = HabitCompletion.objects.get_or_create(
            habit=habit,
            completed_at=today,
            defaults={"note": note},
        )

        if created:
            logger.info(
                "API habit completed: user_id=%s habit_id=%s completion_id=%s completion_date=%s",
                request.user.id,
                habit.pk,
                completion.pk,
                completion.completed_at,
            )
        else:
            logger.info(
                "API habit completion skipped (already completed today): user_id=%s habit_id=%s completion_date=%s",
                request.user.id,
                habit.pk,
                completion.completed_at,
            )

        serializer = HabitCompletionSerializer(
            completion,
            context={"request": request},
        )
        response_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=response_status)

    @action(detail=True, methods=["get"])
    def completions(self, request, pk=None):
        habit = self.get_object()
        queryset = habit.completions.all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = HabitCompletionSerializer(
                page,
                many=True,
                context={"request": request},
            )
            return self.get_paginated_response(serializer.data)

        serializer = HabitCompletionSerializer(
            queryset,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)


class HabitCompletionViewSet(viewsets.ModelViewSet):
    serializer_class = HabitCompletionSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return HabitCompletion.objects.none()
        return HabitCompletion.objects.filter(
            habit__user=self.request.user,
        ).select_related("habit")

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            completion_id = self.kwargs.get(self.lookup_url_kwarg or self.lookup_field)
            completion = (
                HabitCompletion.objects.filter(pk=completion_id)
                .select_related("habit")
                .first()
            )
            if completion is not None and completion.habit.user_id != self.request.user.id:
                logger.warning(
                    "Unauthorized API completion access attempt: user_id=%s completion_id=%s habit_id=%s owner_id=%s",
                    self.request.user.id,
                    completion.pk,
                    completion.habit_id,
                    completion.habit.user_id,
                )
            raise

    def perform_create(self, serializer):
        completion = serializer.save()
        logger.info(
            "API completion created: user_id=%s completion_id=%s habit_id=%s completion_date=%s",
            self.request.user.id,
            completion.pk,
            completion.habit_id,
            completion.completed_at,
        )

    def perform_update(self, serializer):
        completion = serializer.save()
        logger.info(
            "API completion updated: user_id=%s completion_id=%s habit_id=%s completion_date=%s",
            self.request.user.id,
            completion.pk,
            completion.habit_id,
            completion.completed_at,
        )

    def perform_destroy(self, instance):
        logger.warning(
            "API completion deleted: user_id=%s completion_id=%s habit_id=%s completion_date=%s",
            self.request.user.id,
            instance.pk,
            instance.habit_id,
            instance.completed_at,
        )
        instance.delete()
