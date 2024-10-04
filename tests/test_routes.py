import unittest
from unittest.mock import MagicMock, patch

from app.app import create_app
from app.main.services.github_service import GithubService

# pylint: disable=C0411


class TestSubmitDNSRequest(unittest.TestCase):
    def setUp(self):
        self.github_service = MagicMock(GithubService)
        self.logger = MagicMock()
        self.app = create_app(self.github_service, False)
        self.app.config["SECRET_KEY"] = "test_flask"
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.client = self.app.test_client()
        self.form_data = {
            "requestor_name": "g",
            "requestor_email": "g.g@gmail.com",
            "request_details": "g",
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
        self.assertIn("/", response.location)

    @patch("app.main.middleware.auth.requires_auth", return_value=True)
    def test_submit_dns_request_success(self, mock_auth):
        self.login_as_user()
        issue_link = "https://github.com/example/issues/1"
        self.github_service.submit_issue.return_value = issue_link

        response = self.client.post("/create-record", data=self.form_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Request #1", response.data)
