import unittest
from unittest.mock import MagicMock, patch

from flask import session

# pylint: disable=C0411
from slack_sdk.errors import SlackApiError

from app.app import create_app
from app.main.services.github_service import GithubService
from app.main.services.slack_service import SlackService


class TestSubmitDNSRequest(unittest.TestCase):
    def setUp(self):
        self.github_service = MagicMock(GithubService)
        self.slack_service = MagicMock(SlackService)
        self.logger = MagicMock()
        self.app = create_app(self.github_service, self.slack_service, False)
        self.app.config["SECRET_KEY"] = "test_flask"
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.client = self.app.test_client()
        self.form_data = {
            "requestor_name": "g",
            "requestor_email": "g.g@gmail.com",
            "service_owner": "f",
            "service_area": "f",
            "business_area": "hmpps",
            "dns_record": "test.example.com",
            "ttl": "300",
            "record_type": "ns",
            "ns_values": "ns1.example.com, ns2.example.com",
            "record_name": "test",
            "domain_name": "example.com",
        }

    def login_as_user(self):
        """Helper function to set up a logged-in session."""
        with self.client.session_transaction() as sess:
            sess["user"] = "test_user"

    @patch("app.main.middleware.auth.requires_auth", return_value=True)
    def test_create_record_get_authenticated(self, mock_auth):
        self.login_as_user()
        response = self.client.get("/create-record")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Create New DNS Record", response.data)

    def test_create_record_get_unauthenticated(self):
        response = self.client.get("/create-record")
        self.assertEqual(response.status_code, 302)
        # Check the redirect location is to the login page (root in your case "/")
        self.assertIn("/", response.location)

    @patch("app.main.middleware.auth.requires_auth", return_value=True)
    def test_submit_dns_request_success(self, mock_auth):
        self.login_as_user()
        issue_link = "https://github.com/example/issue/1"
        pr_link = "https://github.com/example/pull/1"
        self.github_service.submit_issue.return_value = issue_link
        self.github_service.create_pr.return_value = pr_link

        response = self.client.post("/create-record", data=self.form_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"https://github.com/example/pull/1", response.data)

    @patch("app.main.middleware.auth.requires_auth", return_value=True)
    def test_slack_api_error_handling(self, mock_auth):
        self.login_as_user()
        issue_link = "https://github.com/example/issue/1"
        pr_link = "https://github.com/example/pull/1"
        self.github_service.submit_issue.return_value = issue_link
        self.github_service.create_pr.return_value = pr_link

        # Simulate SlackApiError being raised
        self.slack_service.send_message_to_plaintext_channel_name.side_effect = (
            SlackApiError(
                message="Slack API error",
                response={"ok": False, "error": "invalid_auth"},
            )
        )

        with patch.object(self.app.logger, "error") as mock_logger:
            response = self.client.post("/create-record", data=self.form_data)
            self.assertEqual(response.status_code, 200)
            mock_logger.assert_called_once_with(
                "Failed to send new DNS request notification to slack: Slack API error\nThe server responded with: {'ok': False, 'error': 'invalid_auth'}"
            )
