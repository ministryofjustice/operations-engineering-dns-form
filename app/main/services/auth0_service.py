import logging
from typing import Any
from urllib.parse import quote_plus, urlencode

from auth0.authentication import Users
from auth0.management import Auth0
from authlib.integrations.flask_client import OAuth
from flask import Flask, redirect

logger = logging.getLogger(__name__)


class Auth0_Service:
    def __init__(
        self, app: Flask, client_id: str, client_secret: str, domain: str
    ) -> None:
        self.client_id = client_id
        self.domain = domain
        self.oauth = OAuth(app)
        self.oauth.register(
            "auth0",
            client_id=client_id,
            client_secret=client_secret,
            client_kwargs={
                "scope": "openid profile email",
            },
            server_metadata_url=f"https://{domain}/.well-known/openid-configuration",
        )

        self.users = Users(domain)
        self.auth0_management = Auth0(domain, client_secret)

    def login(self, redirect_uri: str) -> Any:
        return self.oauth.auth0.authorize_redirect(
            redirect_uri=redirect_uri, _external=True
        )

    def get_access_token(self) -> Any:
        return self.oauth.auth0.authorize_access_token()

    def logout(self, redirect_uri: str) -> Any:
        query_parameters = urlencode(
            {
                "returnTo": redirect_uri,
                "client_id": self.client_id,
            },
            quote_via=quote_plus,
        )
        return redirect(f"https://{self.domain}/v2/logout?{query_parameters}")

    def send_magic_link(self, email: str, redirect_uri: str) -> None:
        body = {
            "client_id": self.client_id,
            "connection": "email",
            "email": email,
            "send": "link",
            "authParams": {
                "scope": "openid email profile",
                "redirect_uri": redirect_uri,
            },
        }
        self.auth0_management.jobs.send_verification_email(body)
