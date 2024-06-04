import unittest
from unittest.mock import MagicMock, patch

from app.app import create_app
from app.main.services.github_service import GithubService


class TestSubmitDNSRequest(unittest.TestCase):
    def setUp(self):
        self.github_service = MagicMock(GithubService)
        self.app = create_app(self.github_service, False)
        self.app.config["SECRET_KEY"] = "test_flask"
        self.client = self.app.test_client()
 
    @patch.object(GithubService, "submit_issue")
    def test_submit_dns_request(self, mock_submit_issue):
        form_data = {'requestor_name': '', 'service_owner': '', 'service_area': '', 'business_area': 'hmpps', 'domain_name': '', 'service_description': '', 'domain_purpose': '', 'record_type': 'ns', 'ns_details': ''}
        response = self.app.test_client().post("/submit-dns-request", data=form_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, "/submit-dns-request")
        mock_submit_issue.assert_called_once_with(form_data)

    