from django.contrib import admin

from .models import Habit, HabitCompletion

admin.site.site_header = "Администрирование трекера привычек"
admin.site.site_title = "Трекер привычек"
admin.site.index_title = "Панель управления"


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "frequency", "target_count", "is_active")
    list_filter = ("frequency", "is_active")
    search_fields = ("title", "description", "user__username", "user__email")


@admin.register(HabitCompletion)
class HabitCompletionAdmin(admin.ModelAdmin):
    list_display = ("habit", "completed_at", "created_at")
    list_filter = ("completed_at",)
    search_fields = ("habit__title", "note")
