import logging

from unittest.mock import patch

import httpx

from main import main


def test_main_handles_http_status_error(caplog):
    request = httpx.Request(
        "GET",
        "https://example.com/documents"
    )

    response = httpx.Response(
        status_code=500,
        request=request
    )

    with (
        patch("service.httpx.get", return_value=response),
        patch("service.send_telegram_message") as mock_send,
        patch("service.save_last_document_id") as mock_save,
    ):
        exit_code = main()

    assert "API цирка вернул статус 500" in caplog.text
    assert "Нового расписания нет" not in caplog.text
    assert exit_code == 1

    mock_send.assert_not_called()
    mock_save.assert_not_called()


def test_main_handles_request_error(caplog):
    request = httpx.Request(
        "GET",
        "https://example.com/documents"
    )

    error = httpx.ConnectTimeout(
        "Connection timed out",
        request=request
    )

    with (
        patch("service.httpx.get", side_effect=error),
        patch("service.send_telegram_message") as mock_send,
        patch("service.save_last_document_id") as mock_save,
    ):
        exit_code = main()

    assert "ConnectTimeout" in caplog.text
    assert "Нового расписания нет" not in caplog.text
    assert exit_code == 1

    mock_send.assert_not_called()
    mock_save.assert_not_called()


def test_main_handles_json_decode_error(caplog):
    request = httpx.Request(
        "GET",
        "https://example.com/documents"
    )

    response = httpx.Response(
        status_code=200,
        text="This is not JSON",
        request=request
    )

    with (
        patch("service.httpx.get", return_value=response),
        patch("service.send_telegram_message") as mock_send,
        patch("service.save_last_document_id") as mock_save,
    ):
        exit_code = main()

    assert "API цирка вернул некорректный JSON" in caplog.text
    assert "Нового расписания нет" not in caplog.text
    assert exit_code == 1

    mock_send.assert_not_called()
    mock_save.assert_not_called()


def test_main_returns_zero_when_no_new_schedule(caplog):
    caplog.set_level(logging.INFO)
    with patch("main.check_new_schedule", return_value=False):
        exit_code = main()

    assert exit_code == 0
    assert "Нового расписания нет" in caplog.text


def test_main_returns_zero_when_new_schedule(caplog):
    caplog.set_level(logging.INFO)

    with patch("main.check_new_schedule", return_value=True):
        exit_code = main()

    assert exit_code == 0
    assert "Новое расписание обнаружено, уведомление отправлено" in caplog.text