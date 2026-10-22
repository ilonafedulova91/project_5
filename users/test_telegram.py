import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from users.models import TelegramProfile


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user(
        username="telegram_api_user",
        password="TestPassword123!",
    )


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
def test_connect_telegram(auth_client, user):
    response = auth_client.post(
        "/api/users/telegram/",
        {"chat_id": 123456789},
    )

    assert response.status_code == 200

    profile = TelegramProfile.objects.get(user=user)
    assert profile.chat_id == 123456789


@pytest.mark.django_db
def test_update_telegram_chat_id(auth_client, user):
    TelegramProfile.objects.create(
        user=user,
        chat_id=123456789,
    )

    response = auth_client.post(
        "/api/users/telegram/",
        {"chat_id": 987654321},
    )

    assert response.status_code == 200
    assert TelegramProfile.objects.get(user=user).chat_id == 987654321


@pytest.mark.django_db
def test_telegram_requires_authentication():
    client = APIClient()

    response = client.post(
        "/api/users/telegram/",
        {"chat_id": 123456789},
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_cannot_use_another_users_chat_id(auth_client):
    other_user = get_user_model().objects.create_user(
        username="another_telegram_user",
        password="TestPassword123!",
    )

    TelegramProfile.objects.create(
        user=other_user,
        chat_id=123456789,
    )

    response = auth_client.post(
        "/api/users/telegram/",
        {"chat_id": 123456789},
    )

    assert response.status_code == 400
    assert "chat_id" in response.data
