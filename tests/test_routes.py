import unittest
from unittest.mock import MagicMock

from app.app import create_app
from app.main.services.github_service import GithubService


class TestSubmitDNSRequest(unittest.TestCase):
    def setUp(self):
        self.github_service = MagicMock(GithubService)
        self.app = create_app(self.github_service, False)
        self.app.config["SECRET_KEY"] = "test_flask"
        self.client = self.app.test_client()

    def test_submit_dns_request(self):
        form_data = {
            "requestor_name": "g",
            "requestor_email": "g.g@gmail.com",
            "service_owner": "f",
            "service_area": "f",
            "business_area": "hmpps",
            "domain_name": "example.com",
            "record_name": "test_record",
            "ttl": "300",
            "record_type": "ns",
            "ns_values": "ns1.example.com, ns2.example.com",
        }
        issue_mock = MagicMock()
        issue_mock.html_url = "https://github.com/example/issue/1"
        self.github_service.submit_issue.return_value = issue_mock
        self.github_service.create_pr.return_value = "https://github.com/example/pull/1"

        response = self.client.post("/create-record", data=form_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"https://github.com/example/pull/1", response.data)
        self.github_service.submit_issue.assert_called_once_with(form_data)
        self.github_service.create_pr.assert_called_once_with(form_data, issue_mock)
