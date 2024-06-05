import logging

from github import Github

from app.main.config.app_config import app_config

logger = logging.getLogger(__name__)

class GithubService:
    def __init__(self, org_token: str, repository: str) -> None:
        self.repository = repository
        self.github_client_core_api: Github = Github(org_token)
        self.repo = self.github_client_core_api.get_repo(repository)

    def submit_issue(self, form_data: dict) -> None:
        title = f"[DNS] {form_data['domain_name']}"
        body = (
            f"**Requestor Name:** {form_data['requestor_name']}\n\n"
            f"**Requestor Email:** {form_data['requestor_email']}\n\n"
            f"**MoJ Service Owner:** {form_data['service_owner']}\n\n"
            f"**Service Area Name:** {form_data['service_area']}\n\n"
            f"**Business Area Name:** {form_data['business_area']}\n\n"
            f"**New Domain Name:** {form_data['domain_name']}\n\n"
            f"**New Service Description:** {form_data['service_description']}\n\n"
            f"**Purpose of New Domain:** {form_data['domain_purpose']}\n\n"
            f"**DNS Record Type:** {form_data['record_type']}\n\n"
            f"**NS Details:** {form_data.get('ns_details', 'N/A')}\n\n"
            f"Template request for adding a new justice.gov.uk subdomain."
        )
        labels = ["dns-request", "add-subdomain-request"]

        self.repo.create_issue(
            title=title,
            body=body,
            labels=labels
        )
        logger.info(f"Issue created: {title}")
