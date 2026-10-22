from datetime import timedelta
from unittest.mock import Mock, patch

import pytest
import requests
from django.utils import timezone

from habits.models import Habit
from habits.services import send_telegram_message
from habits.tasks import send_habit_reminders
from users.models import TelegramProfile


@pytest.mark.django_db
def test_telegram_profile(user_factory=None):
    from django.contrib.auth import get_user_model

    user = get_user_model().objects.create_user(
        username="telegramuser",
        password="TestPassword123!",
    )

    profile = TelegramProfile.objects.create(
        user=user,
        chat_id=123456789,
    )

    assert profile.chat_id == 123456789
    assert str(profile)


@patch("habits.services.requests.post")
def test_send_telegram_message(mock_post, settings):
    settings.TELEGRAM_BOT_TOKEN = "fake-test-token"

    mock_response = Mock()
    mock_response.json.return_value = {"ok": True}
    mock_post.return_value = mock_response

    result = send_telegram_message(
        123456789,
        "Test notification",
    )

    assert result["ok"] is True
    mock_post.assert_called_once()


def test_missing_telegram_token(settings):
    settings.TELEGRAM_BOT_TOKEN = ""

    with pytest.raises(ValueError):
        send_telegram_message(123456789, "Test")


@patch("habits.services.requests.post")
def test_telegram_api_error(mock_post, settings):
    settings.TELEGRAM_BOT_TOKEN = "fake-test-token"

    mock_response = Mock()
    mock_response.json.return_value = {
        "ok": False,
        "description": "Bad Request",
    }
    mock_post.return_value = mock_response

    with pytest.raises(ValueError):
        send_telegram_message(123456789, "Test")


@pytest.mark.django_db
@patch("habits.tasks.send_telegram_message")
def test_send_habit_reminder(mock_send):
    from django.contrib.auth import get_user_model

    user = get_user_model().objects.create_user(
        username="reminderuser",
        password="TestPassword123!",
    )

    TelegramProfile.objects.create(
        user=user,
        chat_id=123456789,
    )

    habit = Habit.objects.create(
        user=user,
        place="Home",
        time=(timezone.localtime() - timedelta(minutes=1)).time(),
        action="Drink water",
        duration=60,
        periodicity=1,
    )

    result = send_habit_reminders()

    assert result == 1
    mock_send.assert_called_once()

    habit.refresh_from_db()
    assert habit.last_reminded_at is not None


@pytest.mark.django_db
@patch("habits.tasks.send_telegram_message")
def test_no_duplicate_reminder(mock_send):
    from django.contrib.auth import get_user_model

    user = get_user_model().objects.create_user(
        username="duplicateuser",
        password="TestPassword123!",
    )

    TelegramProfile.objects.create(
        user=user,
        chat_id=123456789,
    )

    Habit.objects.create(
        user=user,
        place="Home",
        time=(timezone.localtime() - timedelta(minutes=1)).time(),
        action="Exercise",
        duration=60,
        periodicity=1,
    )

    assert send_habit_reminders() == 1
    assert send_habit_reminders() == 0
    assert mock_send.call_count == 1


@pytest.mark.django_db
@patch("habits.tasks.send_telegram_message")
def test_reminder_failure(mock_send):
    from django.contrib.auth import get_user_model

    user = get_user_model().objects.create_user(
        username="faileduser",
        password="TestPassword123!",
    )

    TelegramProfile.objects.create(
        user=user,
        chat_id=123456789,
    )

    habit = Habit.objects.create(
        user=user,
        place="Home",
        time=(timezone.localtime() - timedelta(minutes=1)).time(),
        action="Exercise",
        duration=60,
    )

    mock_send.side_effect = requests.RequestException("Telegram unavailable")

    assert send_habit_reminders() == 0

    habit.refresh_from_db()
    assert habit.last_reminded_at is None
