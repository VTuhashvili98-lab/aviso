import pytest
import httpx
import traceback
from unittest.mock import patch

from service import check_new_schedule
from telegram_service import (
    TelegramSendError,
    send_telegram_message,
)


def test_no_tomorrow_schedule():
    with patch("service.get_tomorrow_document_id") as mock_get_id:
        mock_get_id.return_value = None

        result = check_new_schedule()

        assert result is False


def test_schedule_already_exists():
    with (
        patch("service.get_tomorrow_document_id") as mock_get_id,
        patch("service.load_last_document_id") as mock_load_id,
        patch("service.save_last_document_id") as mock_save_id,
    ):
        mock_get_id.return_value = 3380
        mock_load_id.return_value = 3380

        result = check_new_schedule()

        assert result is False
        mock_save_id.assert_not_called()


def test_new_schedule():
    with (
        patch("service.get_tomorrow_document_id") as mock_get_id,
        patch("service.load_last_document_id") as mock_load_id,
        patch("service.save_last_document_id") as mock_save_id,
        patch("service.send_telegram_message") as mock_send_message
    ):
        mock_get_id.return_value = 3380
        mock_load_id.return_value = 3379

        result = check_new_schedule()

        assert result is True
        mock_save_id.assert_called_once_with(3380)
        mock_send_message.assert_called_once_with("Появилось новое расписание!")


def test_telegram_error():
    with (
        patch("service.get_tomorrow_document_id") as mock_get_id,
        patch("service.load_last_document_id") as mock_load_id,
        patch("service.save_last_document_id") as mock_save_id,
        patch("service.send_telegram_message") as mock_send_message,
    ):
        mock_get_id.return_value = 3380
        mock_load_id.return_value = 3379
        mock_send_message.side_effect = ConnectionError("Telegram недоступен")

        with pytest.raises(ConnectionError):
            check_new_schedule()

        mock_send_message.assert_called_once_with("Появилось новое расписание!")
        mock_save_id.assert_not_called()


def test_telegram_http_error():
    request = httpx.Request(
        "POST",
        "https://example.com/send"
    )

    response = httpx.Response(
        status_code=403,
        request=request
    )

    with patch("telegram_service.httpx.post", return_value=response):
        with pytest.raises(
            TelegramSendError,
            match="HTTP-статус 403"
        ):
            send_telegram_message("Тест")


def test_telegram_request_error():
    request = httpx.Request(
        "POST",
        "https://example.com/send"
    )

    error = httpx.ConnectTimeout(
        "Connection timed out",
        request=request
    )

    with patch("telegram_service.httpx.post", side_effect=error):
        with pytest.raises(
            TelegramSendError,
            match="ConnectTimeout"
        ):
            send_telegram_message("Тест")


def test_telegram_error_does_not_expose_token():
    fake_token = "FAKE_SECRET_TOKEN"

    request = httpx.Request(
        "POST",
        f"https://api.telegram.org/bot{fake_token}/sendMessage"
    )

    error = httpx.ConnectTimeout(
        f"Connection failed: {request.url}",
        request=request
    )

    with patch("telegram_service.httpx.post", side_effect=error):
        with pytest.raises(TelegramSendError) as exc_info:
            send_telegram_message("Тест")

    formatted_traceback = "".join(
        traceback.format_exception(exc_info.value)
    )

    assert fake_token not in formatted_traceback