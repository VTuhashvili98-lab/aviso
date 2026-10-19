from unittest.mock import patch

from service import check_new_schedule


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
        patch("service.save_last_document_id") as mock_save_id
    ):
        mock_get_id.return_value = 3380
        mock_load_id.return_value = 3379

        result = check_new_schedule()

        assert result is True
        mock_save_id.assert_called_once_with(3380)
