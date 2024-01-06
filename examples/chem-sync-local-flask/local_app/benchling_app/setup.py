import os
from functools import cache

from benchling_sdk.apps.framework import App
from benchling_sdk.auth.client_credentials_oauth2 import ClientCredentialsOAuth2
from benchling_sdk.benchling import Benchling
from benchling_sdk.models.webhooks.v0 import WebhookEnvelopeV0


def init_app_from_webhook(webhook: WebhookEnvelopeV0) -> App:
    return App(webhook.app.id, _benchling_from_webhook(webhook))


def _benchling_from_webhook(webhook: WebhookEnvelopeV0) -> Benchling:
    return Benchling(webhook.base_url, _auth_method())


@cache
def _auth_method() -> ClientCredentialsOAuth2:
    client_id = os.environ.get("CLIENT_ID")
    assert client_id is not None, "Missing CLIENT_ID from environment"
    client_secret = _client_secret_from_file()
    return ClientCredentialsOAuth2(client_id, client_secret)


def _client_secret_from_file() -> str:
    file_path = os.environ.get("CLIENT_SECRET_FILE")
    assert file_path is not None, "Missing CLIENT_SECRET_FILE from environment"
    with open(file_path) as f:
        return f.read()
