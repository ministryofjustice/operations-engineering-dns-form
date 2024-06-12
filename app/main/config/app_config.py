import os
from types import SimpleNamespace


def __get_env_var(name: str) -> str | None:
    return os.getenv(name)


app_config = SimpleNamespace(
    github=SimpleNamespace(
    repository_name="ministryofjustice/operations-engineering-dns-issues",
    token=__get_env_var("LEV_ADMIN_GITHUB_TOKEN"),
    ),
    flask=SimpleNamespace(
        app_secret_key=__get_env_var("APP_SECRET_KEY"),
    ),
    logging_level=__get_env_var("LOGGING_LEVEL"),
    phase_banner_text=__get_env_var("PHASE_BANNER_TEXT"),
    sentry=SimpleNamespace(
        dsn_key=__get_env_var("SENTRY_DSN_KEY"), environment=__get_env_var("SENTRY_ENV")
    ),
)
