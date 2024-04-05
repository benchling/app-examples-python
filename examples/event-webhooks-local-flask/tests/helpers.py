import json
from pathlib import Path

from benchling_api_client.webhooks.v0.beta.models.webhook_envelope import (
    WebhookEnvelope as WebhookEnvelopeV0Beta,
)


def load_beta_webhook_json(file_path: Path) -> WebhookEnvelopeV0Beta:
    assert file_path.is_file(), f"Missing webhook JSON file at {file_path}"
    with file_path.open() as f:
        webhook_dict = json.loads(f.read())
        return WebhookEnvelopeV0Beta.from_dict(webhook_dict)
