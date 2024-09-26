import os
from types import SimpleNamespace


def __get_env_var(name: str) -> str | None:
    return os.getenv(name)


app_config = SimpleNamespace(
    auth0=SimpleNamespace(
        domain=__get_env_var("AUTH0_DOMAIN"),
        client_id=__get_env_var("AUTH0_CLIENT_ID"),
        client_secret=__get_env_var("AUTH0_CLIENT_SECRET"),
    ),
    github=SimpleNamespace(
        issues_repository="ministryofjustice/operations-engineering-dns-issues",
        pull_request_repository="ministryofjustice/dns",
        project_repository="ministryofjustice/operations-engineering",
        token=__get_env_var("ADMIN_GITHUB_TOKEN"),
    ),
    slack=SimpleNamespace(token=__get_env_var("ADMIN_SLACK_TOKEN")),
    flask=SimpleNamespace(
        app_secret_key=__get_env_var("APP_SECRET_KEY"),
    ),
    logging_level=__get_env_var("LOGGING_LEVEL"),
    phase_banner_text=__get_env_var("PHASE_BANNER_TEXT"),
    sentry=SimpleNamespace(
        dsn_key=__get_env_var("SENTRY_DSN_KEY"), environment=__get_env_var("SENTRY_ENV")
    ),
)
