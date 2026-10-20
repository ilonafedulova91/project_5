import logging
from datetime import datetime

import requests
from celery import shared_task
from django.utils import timezone

from .models import Habit
from .services import send_telegram_message

logger = logging.getLogger(__name__)


@shared_task
def send_habit_reminders():
    now = timezone.localtime()
    today = now.date()

    habits = Habit.objects.filter(
        is_pleasant=False,
        user__telegram_profile__chat_id__isnull=False,
    ).select_related("user__telegram_profile")

    sent = 0

    for habit in habits:
        local_time = timezone.localtime(now, timezone.get_current_timezone())
        scheduled_at = timezone.make_aware(
            datetime.combine(today, habit.time),
            timezone.get_current_timezone(),
        )

        if local_time < scheduled_at:
            continue

        days_since_creation = (today - timezone.localtime(habit.created_at).date()).days

        if days_since_creation < 0:
            continue

        if days_since_creation % habit.periodicity != 0:
            continue

        if habit.last_reminded_at and habit.last_reminded_at >= scheduled_at:
            continue

        message = (
            f"⏰ Напоминание о привычке!\n"
            f"Действие: {habit.action}\n"
            f"Место: {habit.place}\n"
            f"Время: {habit.time:%H:%M}"
        )

        try:
            send_telegram_message(
                habit.user.telegram_profile.chat_id,
                message,
            )
        except (ValueError, requests.RequestException):
            logger.exception("Failed to send reminder for habit %s", habit.pk)
            continue

        habit.last_reminded_at = timezone.now()
        habit.save(update_fields=["last_reminded_at"])
        sent += 1

    return sent
