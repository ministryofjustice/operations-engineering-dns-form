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

    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_select_change_type_create_record(self):
        response = self.client.post(
            "/select-change-type", data={"change_type": "create_record"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "/create-record")

    def test_select_change_type_invalid(self):
        response = self.client.post(
            "/select-change-type", data={"change_type": "invalid"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "/")

    def test_create_record_get(self):
        response = self.client.get("/create-record")
        self.assertEqual(response.status_code, 200)

    @patch("app.main.services.github_service.GithubService.get_hosted_zones")
    def test_create_record_post_valid(self, mock_get_hosted_zones):
        form_data = {
            "requestor_name": "g",
            "requestor_email": "g.g@gmail.com",
            "service_owner": "f",
            "service_area": "f",
            "dns_record": "test.example.com",
            "ttl": "300",
            "record_type": "ns",
            "ns_values": "ns1.example.com",
        }
        mock_get_hosted_zones.return_value = ["example.com"]
        issue_mock = MagicMock()
        issue_mock.number = 1
        self.github_service.submit_issue.return_value = issue_mock
        self.github_service.create_pr.return_value = "https://github.com/example/pull/1"

        response = self.client.post("/create-record", data=form_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"https://github.com/example/pull/1", response.data)
        self.github_service.submit_issue.assert_called_once()
        self.github_service.create_pr.assert_called_once()

    # @patch("app.main.routes.current_app.github_service.get_hosted_zones")
    # def test_create_record_post_invalid_format(self, mock_get_hosted_zones):
    #     form_data = {
    #         "requestor_name": "g",
    #         "requestor_email": "g.g@gmail.com",
    #         "service_owner": "f",
    #         "service_area": "f",
    #         "dns_record": "invalidformat",
    #         "ttl": "300",
    #         "record_type": "ns",
    #         "ns_values": "ns1.example.com, ns2.example.com",
    #     }
    #     mock_get_hosted_zones.return_value = ["example.com"]
    #
    #     response = self.client.post("/create-record", data=form_data)
    #
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b"Invalid DNS record format", response.data)
    #     self.github_service.submit_issue.assert_not_called()
    #     self.github_service.create_pr.assert_not_called()
    #
    # @patch("app.main.routes.current_app.github_service.get_hosted_zones")
    # def test_create_record_post_invalid_domain(self, mock_get_hosted_zones):
    #     form_data = {
    #         "requestor_name": "g",
    #         "requestor_email": "g.g@gmail.com",
    #         "service_owner": "f",
    #         "service_area": "f",
    #         "dns_record": "test.invalid.com",
    #         "ttl": "300",
    #         "record_type": "ns",
    #         "ns_values": "ns1.example.com, ns2.example.com",
    #     }
    #     mock_get_hosted_zones.return_value = ["example.com"]
    #
    #     response = self.client.post("/create-record", data=form_data)
    #
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b"Domain invalid.com does not exist", response.data)
    #     self.github_service.submit_issue.assert_not_called()
    #     self.github_service.create_pr.assert_not_called()
    #
    # @patch("app.main.routes.current_app.github_service.get_hosted_zones")
    # def test_get_hosted_zones(self, mock_get_hosted_zones):
    #     mock_get_hosted_zones.return_value = ["example.com", "test.com"]
    #     response = self.client.get("/api/hosted_zones")
    #
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.json, ["example.com", "test.com"])
    #
    # @patch("app.main.routes.current_app.github_service.get_hosted_zones")
    # def test_get_hosted_zones_error(self, mock_get_hosted_zones):
    #     mock_get_hosted_zones.side_effect = Exception("Error fetching hosted zones")
    #     response = self.client.get("/api/hosted_zones")
    #
    #     self.assertEqual(response.status_code, 500)
    #     self.assertEqual(response.json, {"error": "Error fetching hosted zones"})
    #


if __name__ == "__main__":
    unittest.main()
