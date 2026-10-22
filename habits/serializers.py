from rest_framework import serializers

from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = (
            "id",
            "user",
            "place",
            "time",
            "action",
            "is_pleasant",
            "related_habit",
            "periodicity",
            "reward",
            "duration",
            "is_public",
        )
        read_only_fields = ("id", "user")

    def validate(self, attrs):
        instance = self.instance

        is_pleasant = attrs.get(
            "is_pleasant",
            instance.is_pleasant if instance else False,
        )
        related_habit = attrs.get(
            "related_habit",
            instance.related_habit if instance else None,
        )
        reward = attrs.get(
            "reward",
            instance.reward if instance else None,
        )
        duration = attrs.get(
            "duration",
            instance.duration if instance else None,
        )
        periodicity = attrs.get(
            "periodicity",
            instance.periodicity if instance else 1,
        )

        if related_habit and reward:
            raise serializers.ValidationError(
                "Нельзя указывать одновременно связанную привычку и вознаграждение."
            )

        if duration is not None and duration > 120:
            raise serializers.ValidationError(
                {"duration": "Максимальное время — 120 секунд."}
            )

        if related_habit:
            if not related_habit.is_pleasant:
                raise serializers.ValidationError(
                    {"related_habit": "Привычка должна быть приятной."}
                )

            if related_habit.user_id != self.context["request"].user.id:
                raise serializers.ValidationError(
                    {"related_habit": "Нельзя связывать чужие привычки."}
                )

            if instance and related_habit.pk == instance.pk:
                raise serializers.ValidationError(
                    {"related_habit": "Нельзя связать привычку с собой."}
                )

        if is_pleasant and (reward or related_habit):
            raise serializers.ValidationError(
                "У приятной привычки не может быть вознаграждения "
                "или связанной привычки."
            )

        if (
            instance
            and not is_pleasant
            and Habit.objects.filter(related_habit_id=instance.pk).exists()
        ):
            raise serializers.ValidationError(
                {
                    "is_pleasant": (
                        "Нельзя сделать привычку обычной, "
                        "пока она используется как связанная приятная привычка."
                    )
                }
            )

        if not 1 <= periodicity <= 7:
            raise serializers.ValidationError(
                {"periodicity": "Периодичность должна быть от 1 до 7 дней."}
            )

        return attrs
