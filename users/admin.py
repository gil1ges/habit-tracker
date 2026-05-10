from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            "Дополнительная информация",
            {"fields": ("phone", "avatar", "bio", "created_at")},
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Дополнительная информация",
            {"fields": ("email", "phone", "avatar", "bio")},
        ),
    )
    readonly_fields = ("created_at",)
