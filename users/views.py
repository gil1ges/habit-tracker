import logging

from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.urls import NoReverseMatch, reverse

from users.forms import CustomUserCreationForm

logger = logging.getLogger(__name__)


def _get_post_register_url() -> str:
    try:
        return reverse("habit_list")
    except NoReverseMatch:
        return reverse("home")


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            logger.info("User %s registered successfully.", user.username)
            return redirect(_get_post_register_url())

        logger.warning("Registration failed with errors: %s", form.errors.as_json())
    else:
        form = CustomUserCreationForm()

    return render(request, "users/register.html", {"form": form})
