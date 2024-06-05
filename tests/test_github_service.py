import unittest
from unittest.mock import patch, MagicMock
from app.main.services.github_service import GithubService


@patch("github.Github.__new__")
class TestGithubService(unittest.TestCase):

    def test_submit_issue(self, mock_github):
        mock_repo = MagicMock()
        mock_github_instance = mock_github.return_value
        mock_github_instance.get_repo.return_value = mock_repo

        form_data = {
            'requestor_name': 'John Requestor',
            'requestor_email': 'john.requestor@digital.justice.gov.uk',
            'service_owner': 'Jane Owner',
            'service_area': 'IT Department',
            'business_area': 'HMPPS',
            'domain_name': 'example.justice.gov.uk',
            'service_description': 'A new service description.',
            'domain_purpose': 'Primary purpose of the new domain.',
            'record_type': 'A',
            'ns_details': 'Justification for NS delegation.'
        }

        github_service = GithubService('dummy_token', 'dummy_user/dummy_repo')

        github_service.submit_issue(form_data)

        mock_repo.create_issue.assert_called_once()
        args, kwargs = mock_repo.create_issue.call_args
        self.assertIn('[DNS] example.justice.gov.uk', kwargs['title'])
        self.assertIn('**Requestor Name:** John Requestor', kwargs['body'])
        self.assertIn('**Requestor Email:** john.requestor@digital.justice.gov.uk', kwargs['body'])
        self.assertIn('**MoJ Service Owner:** Jane Owner', kwargs['body'])
        self.assertIn('**Service Area Name:** IT Department', kwargs['body'])
        self.assertIn('**Business Area Name:** HMPPS', kwargs['body'])
        self.assertIn('**New Domain Name:** example.justice.gov.uk', kwargs['body'])
        self.assertIn('**New Service Description:** A new service description.', kwargs['body'])
        self.assertIn('**Purpose of New Domain:** Primary purpose of the new domain.', kwargs['body'])
        self.assertIn('**DNS Record Type:** A', kwargs['body'])
        self.assertIn('**NS Details:** Justification for NS delegation.', kwargs['body'])
        self.assertIn('Template request for adding a new justice.gov.uk subdomain.', kwargs['body'])
        self.assertEqual(kwargs['labels'], ["dns-request", "add-subdomain-request"])


if __name__ == '__main__':
    unittest.main()
