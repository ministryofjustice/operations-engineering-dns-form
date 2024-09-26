# pylint: disable=C0411
import logging

from flask import Flask

from app.main.config.app_config import app_config
from app.main.config.cors_config import configure_cors
from app.main.config.error_handlers_config import configure_error_handlers
from app.main.config.jinja_config import configure_jinja
from app.main.config.limiter_config import configure_limiter
from app.main.config.logging_config import configure_logging
from app.main.config.routes_config import configure_routes
from app.main.config.sentry_config import configure_sentry
from app.main.config.cache_config import configure_cache
from app.main.services.github_service import GithubService
from app.main.services.slack_service import SlackService
from app.main.services.dns_service import DNSService

logger = logging.getLogger(__name__)


def create_app(github_service=None, slack_service=None, dns_service=None, is_rate_limit_enabled=True) -> Flask:
    if github_service is None:
        github_service = GithubService(
            app_config.github.token,
            app_config.github.issues_repository,
            app_config.github.pull_request_repository,
        )
    if slack_service is None:
        slack_service = SlackService(
            app_config.slack.token
        )
    if dns_service is None: 
        dns_service = DNSService()

    configure_logging(app_config.logging_level)

    logger.info("Starting app...")

    app = Flask(__name__, static_folder="static", static_url_path="/assets")

    app.secret_key = app_config.flask.app_secret_key
    app.github_service = github_service
    app.slack_service = slack_service
    app.dns_service = dns_service

    configure_routes(app)
    configure_error_handlers(app)
    configure_sentry(app_config.sentry.dsn_key, app_config.sentry.environment)
    configure_limiter(app, is_rate_limit_enabled)
    configure_jinja(app)
    configure_cors(app)
    configure_cache('SimpleCache', 300, app)

    logger.info("Running app...")

    return app
