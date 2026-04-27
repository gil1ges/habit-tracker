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


class OwnerHabitQuerysetMixin(LoginRequiredMixin):
    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)


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
        context["completion_form"] = HabitCompletionForm(
            initial={"completed_at": timezone.localdate()}
        )
        return context


class HabitCreateView(LoginRequiredMixin, CreateView):
    model = Habit
    form_class = HabitForm
    template_name = "habits/habit_form.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class HabitUpdateView(OwnerHabitQuerysetMixin, UpdateView):
    model = Habit
    form_class = HabitForm
    template_name = "habits/habit_form.html"


class HabitDeleteView(OwnerHabitQuerysetMixin, DeleteView):
    model = Habit
    template_name = "habits/habit_confirm_delete.html"
    success_url = reverse_lazy("habit_list")


@login_required
@require_POST
def habit_complete(request: HttpRequest, pk: int) -> HttpResponse:
    habit = get_object_or_404(Habit, pk=pk)
    if habit.user_id != request.user.id:
        raise Http404("Habit not found.")

    form = HabitCompletionForm(
        request.POST or None,
        initial={"completed_at": timezone.localdate()},
    )

    if form.is_valid():
        HabitCompletion.objects.get_or_create(
            habit=habit,
            completed_at=form.cleaned_data["completed_at"],
            defaults={"note": form.cleaned_data["note"]},
        )
    else:
        HabitCompletion.objects.get_or_create(
            habit=habit,
            completed_at=timezone.localdate(),
        )

    return redirect("habit_detail", pk=habit.pk)
