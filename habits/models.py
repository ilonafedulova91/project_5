from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Habit(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="habits",
    )
    place = models.CharField(max_length=255)
    time = models.TimeField()
    action = models.CharField(max_length=255)
    is_pleasant = models.BooleanField(default=False)
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="related_to",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    periodicity = models.PositiveSmallIntegerField(default=1)
    reward = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    duration = models.PositiveSmallIntegerField()
    last_reminded_at = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
    )
    is_public = models.BooleanField(default=False)

    class Meta:
        ordering = ["time", "id"]
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"

    def clean(self):
        super().clean()

        errors = {}

        if self.related_habit and self.reward:
            errors["reward"] = (
                "Нельзя одновременно указывать вознаграждение и связанную привычку."
            )

        if self.duration is not None and self.duration > 120:
            errors["duration"] = "Время выполнения не может превышать 120 секунд."

        if self.related_habit and not self.related_habit.is_pleasant:
            errors["related_habit"] = "Связанная привычка должна быть приятной."

        if self.is_pleasant and (self.reward or self.related_habit):
            errors["is_pleasant"] = (
                "У приятной привычки не может быть вознаграждения "
                "или связанной привычки."
            )

        if (
            self.pk
            and not self.is_pleasant
            and Habit.objects.filter(related_habit_id=self.pk).exists()
        ):
            errors["is_pleasant"] = (
                "Нельзя сделать привычку обычной, "
                "пока она используется как связанная приятная привычка."
            )

        if self.periodicity is not None and not 1 <= self.periodicity <= 7:
            errors["periodicity"] = "Периодичность должна быть от 1 до 7 дней."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.action} — {self.time}"
