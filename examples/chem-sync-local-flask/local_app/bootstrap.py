import os
from functools import cache

from benchling_sdk.apps.framework import App
from benchling_sdk.benchling import Benchling
from benchling_sdk.auth.client_credentials_oauth2 import ClientCredentialsOAuth2
from benchling_sdk.models.webhooks.v0 import WebhookEnvelopeV0


def init_app_from_webhook(webhook: WebhookEnvelopeV0) -> App:
    return App(webhook.app.id, _benchling_from_webhook(webhook))


def _benchling_from_webhook(webhook: WebhookEnvelopeV0) -> Benchling:
    return Benchling(webhook.base_url, _auth_method())


@cache
def _auth_method() -> ClientCredentialsOAuth2:
    client_id = os.environ["CLIENT_ID"]
    client_secret = os.environ["CLIENT_SECRET"]
    assert client_id is not None, "Missing CLIENT_ID from environment"
    assert client_secret is not None, "Missing CLIENT_SECRET from environment"
    return ClientCredentialsOAuth2(client_id, client_secret)
