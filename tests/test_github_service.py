import unittest
from unittest.mock import MagicMock, patch

import yaml

from github.GithubException import GithubException
from app.main.services.github_service import GithubService

# pylint: disable=W0221
class TestGithubService(unittest.TestCase):

    @patch("app.main.services.github_service.Github")
    def setUp(self, mock_github):
        self.mock_github = mock_github
        self.mock_issues_repo = MagicMock()
        self.mock_pr_repo = MagicMock()
        self.mock_github_instance = mock_github.return_value
        self.mock_github_instance.get_repo.side_effect = [
            self.mock_issues_repo,
            self.mock_pr_repo,
        ]

        self.github_service = GithubService("token", "issues_repo", "pr_repo")
        self.form_data = {
            "requestor_name": "test",
            "requestor_email": "test@test.com",
            "service_owner": "test",
            "service_area": "test",
            "domain_name": "test.com",
            "ttl": "300",
            "record_name": "test",
            "record_type": "a",
            "a_value": "192.0.2.1",
            "deploy_time": "ASAP"
        }

    def test_submitting_an_issue(self):
        mock_issue = MagicMock()
        mock_issue.number = 134
        self.mock_issues_repo.create_issue.return_value = mock_issue

        issue = self.github_service.submit_issue(self.form_data)

        self.mock_issues_repo.create_issue.assert_called_once_with(
            title="[DNS] Add record for test.com",
            body=(
                "**Requestor Name:** test\n\n"
                "**Requestor Email:** test@test.com\n\n"
                "**MoJ Service Owner:** test\n\n"
                "**Service Area Name:** test\n\n"
                "**Domain Name:** test.com\n\n"
                "**TTL:** 300\n\n"
                "**Record Name:** test\n\n"
                "**DNS Record Type:** a\n\n"
                "**A Record Value:** 192.0.2.1\n\n"
                "**Change Date:** ASAP\n\n"
            ),
            labels=["dns-request", "add-record-request"],
        )
        self.assertEqual(issue, "https://github.com/issues_repo/issues/134")

    def test_submit_issue_github_exception(self):

        self.mock_issues_repo.create_issue.side_effect = GithubException(500, "Error creating issue")
        with self.assertRaises(GithubException):
            self.github_service.submit_issue(self.form_data)

        self.mock_issues_repo.create_issue.assert_called_once_with(
            title="[DNS] Add record for test.com",
            body=(
                "**Requestor Name:** test\n\n"
                "**Requestor Email:** test@test.com\n\n"
                "**MoJ Service Owner:** test\n\n"
                "**Service Area Name:** test\n\n"
                "**Domain Name:** test.com\n\n"
                "**TTL:** 300\n\n"
                "**Record Name:** test\n\n"
                "**DNS Record Type:** a\n\n"
                "**A Record Value:** 192.0.2.1\n\n"
                "**Change Date:** ASAP\n\n"
            ),
            labels=["dns-request", "add-record-request"],
        )

    @patch("yaml.safe_load", return_value={})
    def test_create_pr(self, mock_safe_load):
        _ = mock_safe_load
        mock_pull_request = MagicMock()
        mock_pull_request.html_url = "https://github.com/example/pull/1"
        self.mock_pr_repo.create_pull.return_value = mock_pull_request

        issue_link = "https://github.com/issues_repo/issues/134"
        pr_url = self.github_service.create_pr(self.form_data, issue_link)

        branch_name = "add-test.com-record-test"
        self.mock_pr_repo.create_git_ref.assert_called_once_with(
            ref=f"refs/heads/{branch_name}",
            sha=self.mock_pr_repo.get_git_ref.return_value.object.sha,
        )
        self.mock_pr_repo.create_pull.assert_called_once_with(
            title="✨ Add a record to test.com",
            body="This PR connects to https://github.com/issues_repo/issues/134",
            head=branch_name,
            base="main",
        )
        self.assertEqual(pr_url, "https://github.com/example/pull/1")

    def test_create_pr_github_exception(self):

        self.mock_pr_repo.create_git_ref.side_effect = GithubException(500, "Error creating git ref")
        issue_link = "https://github.com/issues_repo/issues/134"
        with self.assertRaises(GithubException):
            self.github_service.create_pr(self.form_data, issue_link)

        self.mock_pr_repo.create_git_ref.assert_called_once_with(
            ref="refs/heads/add-test.com-record-test",
            sha=self.mock_pr_repo.get_git_ref.return_value.object.sha,
        )

    def test_create_pr_with_existing_file(self):
        mock_pull_request = MagicMock()
        mock_pull_request.html_url = "https://github.com/example/pull/1"
        self.mock_pr_repo.create_pull.return_value = mock_pull_request

        mock_content = MagicMock()
        mock_content.decoded_content.decode.return_value = yaml.dump(
            {"existing_record": {"ttl": "300", "type": "A", "value": "192.0.2.2"}}
        )
        self.mock_pr_repo.get_contents.return_value = mock_content

        issue_url = "https://github.com/issues_repo/issues/134"
        pr_url = self.github_service.create_pr(self.form_data, issue_url)

        branch_name = "add-test.com-record-test"
        self.mock_pr_repo.create_git_ref.assert_called_once_with(
            ref=f"refs/heads/{branch_name}",
            sha=self.mock_pr_repo.get_git_ref.return_value.object.sha,
        )
        self.mock_pr_repo.update_file.assert_called_once_with(
            path="hostedzones/test.com.yaml",
            message="✨ Add a record to test.com",
            content=yaml.dump(
                {
                    "existing_record": {
                        "ttl": "300",
                        "type": "A",
                        "value": "192.0.2.2",
                    },
                    "test": {"ttl": "300", "type": "A", "value": "192.0.2.1"},
                },
                default_flow_style=False,
            ),
            sha=mock_content.sha,
            branch=branch_name,
        )
        self.mock_pr_repo.create_pull.assert_called_once_with(
            title="✨ Add a record to test.com",
            body="This PR connects to https://github.com/issues_repo/issues/134",
            head=branch_name,
            base="main",
        )
        self.assertEqual(pr_url, "https://github.com/example/pull/1")


if __name__ == "__main__":
    unittest.main()
