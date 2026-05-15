import logging

from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(user_logged_in)
def log_user_logged_in(sender, request, user, **kwargs):
    logger.info("User %s logged in successfully.", user.username)


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    attempted_username = credentials.get("username", "<unknown>")
    logger.warning("Login failed for username: %s", attempted_username)
