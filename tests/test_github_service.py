import unittest
from unittest.mock import MagicMock, patch

# pylint: disable=C0411
from github.GithubException import GithubException

from app.main.services.github_service import GithubService


class TestGithubService(unittest.TestCase):
    def setUp(self):
        self.mock_github_patcher = patch("app.main.services.github_service.Github")
        self.mock_github = self.mock_github_patcher.start()
        self.mock_issues_repo = MagicMock()
        self.mock_pr_repo = MagicMock()
        self.mock_github_instance = self.mock_github.return_value
        self.mock_github_instance.get_repo.side_effect = [
            self.mock_issues_repo,
            self.mock_pr_repo,
        ]

        self.github_service = GithubService("token", "issues_repo", "pr_repo")
        self.form_data = {
            "requestor_name": "test",
            "requestor_email": "test@test.com",
            "request_details": "Some more details",
        }

    def tearDown(self):
        # Stop patching to clean up after tests
        self.mock_github_patcher.stop()

    def test_submitting_an_issue(self):
        mock_issue = MagicMock()
        mock_issue.number = 134
        self.mock_issues_repo.create_issue.return_value = mock_issue

        issue = self.github_service.submit_issue(self.form_data)

        self.mock_issues_repo.create_issue.assert_called_once_with(
            title="🌎 DNS Change Request by test",
            body=(
                "**Requestor Name:** test\n\n"
                "**Requestor Email:** test@test.com\n\n"
                "**Request Detail:** Some more details\n\n"
            ),
            labels=["dns-request", "add-record-request"],
        )
        self.assertEqual(issue, "https://github.com/issues_repo/issues/134")

    def test_submit_issue_github_exception(self):

        self.mock_issues_repo.create_issue.side_effect = GithubException(
            500, "Error creating issue"
        )
        with self.assertRaises(GithubException):
            self.github_service.submit_issue(self.form_data)

        self.mock_issues_repo.create_issue.assert_called_once_with(
            title="🌎 DNS Change Request by test",
            body=(
                "**Requestor Name:** test\n\n"
                "**Requestor Email:** test@test.com\n\n"
                "**Request Detail:** Some more details\n\n"
            ),
            labels=["dns-request", "add-record-request"],
        )


if __name__ == "__main__":
    unittest.main()
