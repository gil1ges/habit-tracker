from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from rest_framework import serializers

from habits.models import Habit, HabitCompletion
from habits.validators import (
    validate_color,
    validate_forbidden_words,
    validate_habit_title,
    validate_target_count,
)

User = get_user_model()


def _run_django_validator(validator, value):
    try:
        validator(value)
    except DjangoValidationError as exc:
        raise serializers.ValidationError(exc.messages) from exc


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "phone", "password", "password2"]
        read_only_fields = ["id"]
        extra_kwargs = {
            "email": {"required": True},
            "phone": {"required": False, "allow_blank": True},
        }

    def validate_username(self, value):
        username = value.strip()
        if len(username) < 5:
            raise serializers.ValidationError(
                "Username must contain at least 5 characters."
            )
        return username

    def validate_email(self, value):
        email = value.strip()
        if not email:
            raise serializers.ValidationError("Email is required.")
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return email

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password2": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "phone", "bio", "avatar", "created_at"]
        read_only_fields = ["id", "created_at"]


class HabitSerializer(serializers.ModelSerializer):
    completion_count = serializers.SerializerMethodField()
    last_completed = serializers.SerializerMethodField()

    class Meta:
        model = Habit
        fields = [
            "id",
            "title",
            "description",
            "frequency",
            "target_count",
            "color",
            "is_active",
            "completion_count",
            "last_completed",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "completion_count",
            "last_completed",
            "created_at",
            "updated_at",
        ]

    def get_completion_count(self, obj):
        completion_count = getattr(obj, "completion_count", None)
        if completion_count is not None:
            return completion_count
        return obj.completions.count()

    def get_last_completed(self, obj):
        last_completed = getattr(obj, "last_completed", None)
        if last_completed is None:
            last_completed = (
                obj.completions.order_by("-completed_at")
                .values_list("completed_at", flat=True)
                .first()
            )
        return last_completed.isoformat() if last_completed else None

    def validate_title(self, value):
        title = value.strip()
        _run_django_validator(validate_habit_title, title)
        _run_django_validator(validate_forbidden_words, title)
        return title

    def validate_description(self, value):
        description = value.strip()
        if description:
            _run_django_validator(validate_forbidden_words, description)
        return description

    def validate_target_count(self, value):
        _run_django_validator(validate_target_count, value)
        return value

    def validate_color(self, value):
        color = value.strip()
        _run_django_validator(validate_color, color)
        return color

    def validate(self, attrs):
        instance = self.instance
        frequency = attrs.get(
            "frequency",
            instance.frequency if instance else Habit.FrequencyChoices.DAILY,
        )
        target_count = attrs.get(
            "target_count",
            instance.target_count if instance else Habit._meta.get_field("target_count").default,
        )
        is_active = attrs.get(
            "is_active",
            instance.is_active if instance else Habit._meta.get_field("is_active").default,
        )
        description = attrs.get(
            "description",
            instance.description if instance else "",
        )

        if frequency == Habit.FrequencyChoices.DAILY and target_count > 7:
            raise serializers.ValidationError(
                {
                    "target_count": (
                        "Daily habits cannot have a target count greater than 7."
                    )
                }
            )

        if is_active is False and not description:
            raise serializers.ValidationError(
                {"description": "Inactive habits must include a description."}
            )

        return attrs


class HabitCompletionSerializer(serializers.ModelSerializer):
    habit_title = serializers.CharField(source="habit.title", read_only=True)
    completed_at = serializers.DateField(required=False)

    class Meta:
        model = HabitCompletion
        fields = ["id", "habit", "habit_title", "completed_at", "note", "created_at"]
        read_only_fields = ["id", "habit_title", "created_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            self.fields["habit"].queryset = Habit.objects.filter(user=request.user)
        else:
            self.fields["habit"].queryset = Habit.objects.none()

    def validate_completed_at(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError("Completion date cannot be in the future.")
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        instance = self.instance
        habit = attrs.get("habit", instance.habit if instance else None)
        completed_at = attrs.get(
            "completed_at",
            instance.completed_at if instance else timezone.localdate(),
        )

        if user and user.is_authenticated and habit and habit.user_id != user.id:
            raise serializers.ValidationError(
                {"habit": "You can only create completions for your own habits."}
            )

        if habit and HabitCompletion.objects.filter(
            habit=habit,
            completed_at=completed_at,
        ).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError(
                {
                    "completed_at": (
                        "This habit already has a completion for this date."
                    )
                }
            )

        return attrs
