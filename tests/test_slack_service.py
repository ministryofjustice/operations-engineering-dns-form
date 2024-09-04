import unittest
from unittest.mock import MagicMock, patch

from app.main.services.slack_service import SlackService


class TestSendMessageToPlainTextChannelName(unittest.TestCase):

    @patch("logging.info")
    @patch("slack_sdk.WebClient.__new__")
    def setUp(self, mock_web_client, mock_logging_info):
        self.channel_name = 'test_channel'
        self.message = 'test message'
        self.channel_id = 'test_channel_id'
        self.response_metadata = {'next_cursor': ''}
        self.channel = {'name': self.channel_name, 'id': self.channel_id}
        self.response_ok = {'ok': True}
        self.slack_client = MagicMock()
        self.mock_web_client = mock_web_client
        self.mock_web_client.return_value = self.slack_client
        self.slack_service = SlackService("")
        self.slack_client.conversations_list.return_value = {
            'channels': [self.channel], 'response_metadata': self.response_metadata}
        self.slack_service.slack_client = self.slack_client
        self.mock_logging_info = mock_logging_info

    def test_send_message_to_plaintext_channel_name(self):
        self.slack_client.chat_postMessage.return_value = self.response_ok
        self.slack_service.send_message_to_plaintext_channel_name(
            self.message, self.channel_name)
        self.slack_client.chat_postMessage.assert_called_once_with(
            channel=self.channel_id, text=self.message)

    def test_send_message_to_plaintext_channel_name_when_no_channel_name_exists(self):
        response = {'channels': [],
                    'response_metadata': self.response_metadata}
        self.slack_client.conversations_list.return_value = response
        self.slack_service.send_message_to_plaintext_channel_name(
            self.message, self.channel_name)
        self.slack_client.chat_postMessage.assert_not_called()

    def test_send_message_to_plaintext_channel_name_when_response_not_okay(self):
        response = {'ok': False, "error": "some-error"}
        self.slack_client.chat_postMessage.return_value = response
        self.slack_service.send_message_to_plaintext_channel_name(
            self.message, self.channel_name)
        self.slack_client.chat_postMessage.assert_called_once_with(
            channel=self.channel_id, text=self.message)

    def test_lookup_channel_id(self):
        result = self.slack_service._lookup_channel_id(self.channel_name)
        self.slack_client.conversations_list.assert_called_once_with(
            limit=200, cursor='')
        self.assertEqual(result, self.channel_id)

    def test_lookup_channel_id_when_no_matching_channels(self):
        response = {'channels': [
            {'name': "other-channel", 'id': self.channel_id}], 'response_metadata': self.response_metadata}
        self.slack_client.conversations_list.return_value = response
        result = self.slack_service._lookup_channel_id(self.channel_name)
        self.slack_client.conversations_list.assert_called_once_with(
            limit=200, cursor='')
        self.assertIsNone(result)

    def test_lookup_channel_id_when_channels_empty(self):
        response = {'channels': [],
                    'response_metadata': self.response_metadata}
        self.slack_client.conversations_list.return_value = response
        result = self.slack_service._lookup_channel_id(self.channel_name)
        self.slack_client.conversations_list.assert_called_once_with(
            limit=200, cursor='')
        self.assertIsNone(result)

    def test_lookup_channel_id_when_no_channels(self):
        response = {'response_metadata': self.response_metadata}
        self.slack_client.conversations_list.return_value = response
        result = self.slack_service._lookup_channel_id(self.channel_name)
        self.slack_client.conversations_list.assert_called_once_with(
            limit=200, cursor='')
        self.assertIsNone(result)
