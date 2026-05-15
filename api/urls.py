from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import MeAPIView, RegisterAPIView

urlpatterns = [
    path("auth/register/", RegisterAPIView.as_view(), name="api-register"),
    path("auth/token/", TokenObtainPairView.as_view(), name="api-token-obtain"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="api-token-refresh"),
    path("users/me/", MeAPIView.as_view(), name="api-users-me"),
]
