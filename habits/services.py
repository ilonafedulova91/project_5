import requests
from django.conf import settings


def send_telegram_message(chat_id, text):
    if not settings.TELEGRAM_BOT_TOKEN:
        raise ValueError("Telegram bot token is not configured.")

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"

    response = requests.post(
        url,
        json={
            "chat_id": chat_id,
            "text": text,
        },
        timeout=10,
    )
    response.raise_for_status()

    result = response.json()
    if not result.get("ok"):
        raise ValueError(result.get("description", "Telegram API error"))

    return result
