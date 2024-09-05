import unittest
from unittest.mock import MagicMock, patch

from app.main.services.slack_service import SlackService


class TestSendMessageToPlainTextChannelName(unittest.TestCase):

    CHANNEL_NAME = "test_channel"
    MESSAGE = "test message"
    CHANNEL_ID = "test_channel_id"
    RESPONSE_METADATA = {"next_cursor": ""}
    RESPONSE_OK = {"ok": True}
    RESPONSE_ERROR = {'ok': False, "error": "some-error"}

    def setUp(self):
        self.channel = {'name': self.CHANNEL_NAME, 'id': self.CHANNEL_ID}
        self.slack_client = MagicMock()
        self.slack_service = SlackService("test_slack_token")
        self.slack_client.conversations_list.return_value = {
            'channels': [self.channel], 'response_metadata': self.RESPONSE_METADATA}
        self.slack_service.slack_client = self.slack_client

    @patch("logging.info")
    def test_send_message_to_plaintext_channel_name(self, mock_logging_info):
        self.slack_client.chat_postMessage.return_value = self.RESPONSE_OK
        self.slack_service.send_message_to_plaintext_channel_name(
            self.MESSAGE, self.CHANNEL_NAME)
        self.slack_client.chat_postMessage.assert_called_once_with(
            channel=self.CHANNEL_ID, text=self.MESSAGE)
        mock_logging_info.assert_called_once_with("Message sent to channel %s", self.CHANNEL_NAME)

    @patch("logging.error")
    def test_send_message_to_plaintext_channel_name_when_no_channel_name_exists(self, mock_logging_error):
        response = {'channels': [],
                    'response_metadata': self.RESPONSE_METADATA}
        self.slack_client.conversations_list.return_value = response
        self.slack_service.send_message_to_plaintext_channel_name(
            self.MESSAGE, self.CHANNEL_NAME)
        self.slack_client.chat_postMessage.assert_not_called()
        mock_logging_error.assert_called_once_with("Could not find channel %s", self.CHANNEL_NAME)

    @patch("logging.error")
    def test_send_message_to_plaintext_channel_name_when_response_not_okay(self, mock_logging_error):
        self.slack_client.chat_postMessage.return_value = self.RESPONSE_ERROR
        self.slack_service.send_message_to_plaintext_channel_name(
            self.MESSAGE, self.CHANNEL_NAME)
        self.slack_client.chat_postMessage.assert_called_once_with(
            channel=self.CHANNEL_ID, text=self.MESSAGE)
        mock_logging_error.assert_called_once_with("Error sending message to channel %s: %s",
                                                   self.CHANNEL_NAME, self.RESPONSE_ERROR['error'])

    def test_lookup_channel_id(self):
        result = self.slack_service.lookup_channel_id(self.CHANNEL_NAME)
        self.slack_client.conversations_list.assert_called_once_with(
            limit=200, cursor='')
        self.assertEqual(result, self.CHANNEL_ID)

    def test_lookup_channel_id_when_no_matching_channels(self):
        response = {'channels': [
            {'name': "other-channel", 'id': self.CHANNEL_ID}], 'response_metadata': self.RESPONSE_METADATA}
        self.slack_client.conversations_list.return_value = response
        result = self.slack_service.lookup_channel_id(self.CHANNEL_NAME)
        self.slack_client.conversations_list.assert_called_once_with(
            limit=200, cursor='')
        self.assertIsNone(result)

    def test_lookup_channel_id_when_channels_empty(self):
        response = {'channels': [],
                    'response_metadata': self.RESPONSE_METADATA}
        self.slack_client.conversations_list.return_value = response
        result = self.slack_service.lookup_channel_id(self.CHANNEL_NAME)
        self.slack_client.conversations_list.assert_called_once_with(
            limit=200, cursor='')
        self.assertIsNone(result)

    def test_lookup_channel_id_when_no_channels(self):
        response = {'response_metadata': self.RESPONSE_METADATA}
        self.slack_client.conversations_list.return_value = response
        result = self.slack_service.lookup_channel_id(self.CHANNEL_NAME)
        self.slack_client.conversations_list.assert_called_once_with(
            limit=200, cursor='')
        self.assertIsNone(result)
