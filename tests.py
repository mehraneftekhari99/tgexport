import unittest
from unittest.mock import patch, MagicMock, mock_open
import tgexport


class TestTGExport(unittest.TestCase):
    # Test when there are no previous messages
    @patch("tgexport.os")
    @patch("tgexport.TelegramClient")
    @patch("builtins.open", new_callable=mock_open)
    def test_no_previous_messages(self, mock_open, mock_TelegramClient, mock_os):
        # Mock the os functions
        mock_os.makedirs.return_value = None
        mock_os.environ.get.return_value = "test"
        mock_os.listdir.return_value = []

        # Mock the TelegramClient functions
        mock_message = MagicMock()
        mock_message.text = "test message"
        mock_message.id = 1
        mock_message.date.strftime.return_value = "2022-01-01"
        mock_TelegramClient.return_value.__enter__.return_value.get_messages.return_value = [
            mock_message
        ]
        mock_TelegramClient.return_value.__enter__.return_value.iter_messages.return_value = [
            mock_message
        ]

        # Call the function
        tgexport.export_channel_messages("test_channel", "test_api_id", "test_api_hash")

        # Check the results
        mock_os.makedirs.assert_called_once_with("data/test_channel", exist_ok=True)
        mock_TelegramClient.assert_called_once_with("anon", "test_api_id", "test_api_hash")
        mock_os.listdir.assert_called_once_with("data/test_channel")
        mock_open.assert_called_once_with("data/test_channel/2022-01-01-0000000001.txt", "w")

    # Test when there are previous messages
    @patch("tgexport.os")
    @patch("tgexport.TelegramClient")
    @patch("builtins.open", new_callable=mock_open)
    def test_previous_messages(self, mock_open, mock_TelegramClient, mock_os):
        mock_os.makedirs.return_value = None
        mock_os.environ.get.return_value = "test"
        mock_os.listdir.return_value = ["2022-01-01-0000000001.txt"]

        mock_message_old = MagicMock()
        mock_message_old.text = "test message old"
        mock_message_old.id = 1
        mock_message_old.date.strftime.return_value = "2022-01-01"

        mock_message_new = MagicMock()
        mock_message_new.text = "test message new"
        mock_message_new.id = 2
        mock_message_new.date.strftime.return_value = "2022-01-02"

        mock_TelegramClient.return_value.__enter__.return_value.get_messages.return_value = [
            mock_message_new
        ]
        mock_TelegramClient.return_value.__enter__.return_value.iter_messages.return_value = [
            mock_message_new
        ]

        tgexport.export_channel_messages("test_channel", "test_api_id", "test_api_hash")

        mock_os.makedirs.assert_called_once_with("data/test_channel", exist_ok=True)
        mock_TelegramClient.assert_called_once_with("anon", "test_api_id", "test_api_hash")
        mock_os.listdir.assert_called_once_with("data/test_channel")
        mock_open.assert_called_once_with("data/test_channel/2022-01-02-0000000002.txt", "w")


if __name__ == "__main__":
    unittest.main()
