from django.conf import settings
from django.db import models


class TelegramProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="telegram_profile",
    )
    chat_id = models.BigIntegerField(
        unique=True,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Telegram profile: {self.user}"
