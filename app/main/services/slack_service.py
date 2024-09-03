from slack_sdk import WebClient
import logging


class SlackService:

    # Added to stop TypeError on instantiation. See https://github.com/python/cpython/blob/d2340ef25721b6a72d45d4508c672c4be38c67d3/Objects/typeobject.c#L4444
    def __new__(cls, *args, **kwargs):
        return super(SlackService, cls).__new__(cls)

    def __init__(self, slack_token: str) -> None:
        self.slack_client = WebClient(slack_token)


    def send_message_to_plaintext_channel_name(self, message, channel_name: str):
        """
        Sends a message to a plaintext channel by name.

        Args:
            message (str): The message to send.
            channel_name (str): The name of the channel to send the message to.
        """
        channel_id = self._lookup_channel_id(channel_name)
        if channel_id is None:
            logging.error("Could not find channel %s", channel_name)
        else:
            response = self.slack_client.chat_postMessage(
                channel=channel_id, text=message)
            if not response['ok']:
                logging.error("Error sending message to channel %s: %s",
                              channel_name, response['error'])
            else:
                logging.info("Message sent to channel %s", channel_name)

    def _lookup_channel_id(self, channel_name, cursor=''):
        channel_id = None
        response = self.slack_client.conversations_list(
            limit=200, cursor=cursor)

        if response['channels'] is not None:
            for channel in response['channels']:
                if channel['name'] == channel_name:
                    channel_id = channel['id']
                    break

        if channel_id is None and response['response_metadata']['next_cursor'] != '':
            channel_id = self._lookup_channel_id(
                channel_name, cursor=response['response_metadata']['next_cursor'])

        return channel_id
