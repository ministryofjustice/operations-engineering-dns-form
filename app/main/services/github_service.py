import logging

import yaml
from github import Github
from github.GithubException import GithubException

logger = logging.getLogger(__name__)


# pylint: disable=R0903
class GithubService:
    def __init__(
        self, org_token: str, issues_repository: str, pull_request_repository: str
    ) -> None:
        self.issues_repository = issues_repository
        self.pull_request_repository = pull_request_repository
        self.github_client_core_api: Github = Github(org_token)
        self.issues_repo = self.github_client_core_api.get_repo(issues_repository)
        self.pr_repo = self.github_client_core_api.get_repo(pull_request_repository)

    def submit_issue(self, form_data: dict) -> int:
        title = f"[DNS] Add record for {form_data['domain_name']}"
        body = (
            f"**Requestor Name:** {form_data['requestor_name']}\n\n"
            f"**Requestor Email:** {form_data['requestor_email']}\n\n"
            f"**MoJ Service Owner:** {form_data['service_owner']}\n\n"
            f"**Service Area Name:** {form_data['service_area']}\n\n"
            f"**Domain Name:** {form_data['domain_name']}\n\n"
            f"**TTL:** {form_data['ttl']}\n\n"
            f"**Record Name:** {form_data['record_name']}\n\n"
            f"**DNS Record Type:** {form_data['record_type']}\n\n"
        )

        if form_data["record_type"] == "ns":
            body += f"**NS Values:** {form_data['ns_values']}\n\n"
        elif form_data["record_type"] == "a":
            body += f"**A Record Value:** {form_data['a_value']}\n\n"
        elif form_data["record_type"] == "mx":
            body += f"**MX Values:** {form_data['mx_values']}\n\n"
        elif form_data["record_type"] == "cname":
            body += f"**CNAME Value:** {form_data['cname_value']}\n\n"
        elif form_data["record_type"] == "txt":
            body += f"**TXT Value:** {form_data['txt_value']}\n\n"
        elif form_data["record_type"] == "alias":
            body += (
                f"**Evaluate Target Health:** {form_data['evaluate_target_health']}\n\n"
                f"**Hosted Zone ID:** {form_data['hosted_zone_id']}\n\n"
                f"**Alias Name:** {form_data['alias_name']}\n\n"
                f"**Alias Type:** {form_data['alias_type']}\n\n"
            )

        body += "Template request for adding a new DNS record."

        labels = ["dns-request", "add-record-request"]

        try:
            issue = self.issues_repo.create_issue(title=title, body=body, labels=labels)
            logger.info("Issue created: %s", title)
            return issue.number
        except GithubException as e:
            logger.error("Error creating issue: %s", e)
            raise

    def create_pr(self, form_data: dict, issue_number) -> str:
        branch_name = (
            f"add-{form_data['domain_name']}-record-{form_data['record_name']}"
        )
        issue_number = (
            f"https://github.com/{self.issues_repository}/issues/{issue_number}"
        )
        file_path = f"hostedzones/{form_data['domain_name']}.yaml"

        record_name = form_data["record_name"]
        record_data = {
            "ttl": form_data["ttl"],
            "type": (form_data["record_type"].upper()),
        }

        if form_data["record_type"] == "ns":
            record_data["values"] = form_data["ns_values"].split(",")
        elif form_data["record_type"] == "a":
            record_data["value"] = form_data["a_value"]
        elif form_data["record_type"] == "mx":
            record_data["values"] = form_data["mx_values"].split("\n")
        elif form_data["record_type"] == "cname":
            record_data["value"] = form_data["cname_value"]
        elif form_data["record_type"] == "txt":
            record_data["value"] = form_data["txt_value"]
        elif form_data["record_type"] == "alias":
            record_data["value"] = {
                "evaluate-target-health": form_data["evaluate_target_health"].lower()
                == "true",
                "hosted-zone-id": form_data["hosted_zone_id"],
                "name": form_data["alias_name"],
                "type": form_data["alias_type"],
            }

        main_ref = self.pr_repo.get_git_ref("heads/main")
        main_sha = main_ref.object.sha
        self.pr_repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=main_sha)

        try:
            existing_content = self.pr_repo.get_contents(file_path, ref="main")
            file_content = existing_content.decoded_content.decode("utf-8")
            yaml_content = yaml.safe_load(file_content)
        except GithubException:
            yaml_content = {}

        yaml_content[record_name] = record_data

        sorted_yaml_content = dict(sorted(yaml_content.items()))

        new_file_content = yaml.dump(sorted_yaml_content, default_flow_style=False)

        commit_message = (
            f"✨ Add {form_data['record_type']} record to {form_data['domain_name']}"
        )
        if "existing_content" in locals():
            self.pr_repo.update_file(
                path=file_path,
                message=commit_message,
                content=new_file_content,
                sha=existing_content.sha,
                branch=branch_name,
            )
        else:
            self.pr_repo.create_file(
                path=file_path,
                message=commit_message,
                content=new_file_content,
                branch=branch_name,
            )

        pr = self.pr_repo.create_pull(
            title=f"✨ Add {form_data['record_type']} record to {form_data['domain_name']}",
            body=f"Resolves {issue_number}",
            head=branch_name,
            base="main",
        )
        logger.info("Pull request created: %s", pr.html_url)
        return pr.html_url
