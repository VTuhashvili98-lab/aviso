import os
import logging
import httpx

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


class TelegramSendError(Exception):
    pass


def send_telegram_message(message: str) -> None:
    if not BOT_TOKEN or not BOT_TOKEN.strip():
        raise TelegramSendError("Не задан BOT_TOKEN")

    if not CHAT_ID or not CHAT_ID.strip():
        raise TelegramSendError("Не задан CHAT_ID")

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}

    try:
        response = httpx.post(url=url, json=payload, timeout=10)
        response.raise_for_status()

    except httpx.HTTPStatusError as exc:
        raise TelegramSendError(
            f"Telegram API вернул HTTP-статус {exc.response.status_code}"
        ) from None

    except httpx.RequestError as exc:
        raise TelegramSendError(
            f"Ошибка соединения с Telegram API: {type(exc).__name__}"
        ) from None

    logging.info(
        "Telegram API: POST /sendMessage — %s %s",
        response.status_code,
        response.reason_phrase
    )
