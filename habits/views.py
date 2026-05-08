import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import HabitCompletionForm, HabitForm
from .models import Habit, HabitCompletion

logger = logging.getLogger(__name__)


class OwnerHabitQuerysetMixin(LoginRequiredMixin):
    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)

    def get_object(self, queryset=None):
        queryset = queryset or self.get_queryset()
        pk = self.kwargs.get("pk")
        target_habit = Habit.objects.filter(pk=pk).select_related("user").first()

        if target_habit is None:
            raise Http404("Habit not found.")

        if target_habit.user_id != self.request.user.id:
            logger.warning(
                "Unauthorized habit access attempt: user_id=%s habit_id=%s owner_id=%s",
                self.request.user.id,
                target_habit.pk,
                target_habit.user_id,
            )
            raise Http404("Habit not found.")

        return queryset.get(pk=pk)


class HabitListView(LoginRequiredMixin, ListView):
    model = Habit
    template_name = "habits/habit_list.html"
    context_object_name = "habits"

    def get_queryset(self):
        return self.request.user.habits.all()


class HabitDetailView(OwnerHabitQuerysetMixin, DetailView):
    model = Habit
    template_name = "habits/habit_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        completion_form = HabitCompletionForm(
            initial={"completed_at": timezone.localdate()}
        )
        completion_form.fields["completed_at"].widget.attrs["readonly"] = "readonly"
        context["completion_form"] = completion_form
        return context


class HabitCreateView(LoginRequiredMixin, CreateView):
    model = Habit
    form_class = HabitForm
    template_name = "habits/habit_form.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        logger.info(
            "Habit created: user_id=%s habit_id=%s title=%s",
            self.request.user.id,
            self.object.pk,
            self.object.title,
        )
        return response


class HabitUpdateView(OwnerHabitQuerysetMixin, UpdateView):
    model = Habit
    form_class = HabitForm
    template_name = "habits/habit_form.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        logger.info(
            "Habit updated: user_id=%s habit_id=%s title=%s",
            self.request.user.id,
            self.object.pk,
            self.object.title,
        )
        return response


class HabitDeleteView(OwnerHabitQuerysetMixin, DeleteView):
    model = Habit
    template_name = "habits/habit_confirm_delete.html"
    success_url = reverse_lazy("habit_list")

    def form_valid(self, form):
        self.object = self.get_object()
        logger.warning(
            "Habit deleted: user_id=%s habit_id=%s title=%s",
            self.request.user.id,
            self.object.pk,
            self.object.title,
        )
        return super().form_valid(form)


@login_required
@require_POST
def habit_complete(request: HttpRequest, pk: int) -> HttpResponse:
    habit = get_object_or_404(Habit.objects.select_related("user"), pk=pk)
    if habit.user_id != request.user.id:
        logger.warning(
            "Unauthorized habit access attempt: user_id=%s habit_id=%s owner_id=%s",
            request.user.id,
            habit.pk,
            habit.user_id,
        )
        raise Http404("Habit not found.")

    note = request.POST.get("note", "").strip()
    completion, created = HabitCompletion.objects.get_or_create(
        habit=habit,
        completed_at=timezone.localdate(),
        defaults={"note": note},
    )

    if created:
        logger.info(
            "Habit completed: user_id=%s habit_id=%s completion_date=%s",
            request.user.id,
            habit.pk,
            completion.completed_at,
        )
    else:
        logger.info(
            "Habit completion skipped (already completed today): user_id=%s habit_id=%s completion_date=%s",
            request.user.id,
            habit.pk,
            completion.completed_at,
        )

    return redirect("habit_detail", pk=habit.pk)
