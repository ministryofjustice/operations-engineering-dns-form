import unittest
from unittest.mock import MagicMock, patch

from app.main.services.github_service import GithubService


class TestGithubService(unittest.TestCase):
    @patch("app.main.services.github_service.Github")
    def test_submitting_an_issue(self, mock_github):
        mock_repository = MagicMock()
        mock_github_instance = mock_github.return_value
        mock_github_instance.get_repo.return_value = mock_repository

        mock_issue = MagicMock()
        mock_issue.number = 134
        mock_repository.create_issue.return_value = mock_issue

        github_service = GithubService("token", "issues_repo", "pr_repo")
        form_data = {
            "requestor_name": "test",
            "requestor_email": "test@test.com",
            "service_owner": "test",
            "service_area": "test",
            "domain_name": "test.com",
            "ttl": "300",
            "record_name": "test",
            "record_type": "a",
            "a_value": "192.0.2.1",
        }

        issue = github_service.submit_issue(form_data)

        mock_repository.create_issue.assert_called_once()
        self.assertEqual(issue, 134)


if __name__ == "__main__":
    unittest.main()
