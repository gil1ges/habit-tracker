from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    HabitCompletionViewSet,
    HabitViewSet,
    MeAPIView,
    RegisterAPIView,
)

router = DefaultRouter()
router.register("habits", HabitViewSet, basename="api-habits")
router.register("completions", HabitCompletionViewSet, basename="api-completions")

urlpatterns = [
    path("auth/register/", RegisterAPIView.as_view(), name="api-register"),
    path("auth/token/", TokenObtainPairView.as_view(), name="api-token-obtain"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="api-token-refresh"),
    path("users/me/", MeAPIView.as_view(), name="api-users-me"),
    path("", include(router.urls)),
]
