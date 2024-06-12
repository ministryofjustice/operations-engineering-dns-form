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
        form_data = {'requestor_name': 'g', 'requestor_email': 'g.g@gmail.com', 'service_owner': 'f', 'service_area': 'f', 'business_area': 'hmpps', 'domain_name': 'f', 'service_description': 'f', 'domain_purpose': 'f', 'record_type': 'ns', 'ns_details': ''}
        response = self.client.post("/submit-dns-request", data=form_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, "/submit-dns-request")
        self.github_service.submit_issue.assert_called_once_with(form_data)
