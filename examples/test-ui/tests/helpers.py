import json
from pathlib import Path

from benchling_sdk.models.webhooks.v0 import WebhookEnvelopeV0


def load_webhook_json(file_path: Path) -> WebhookEnvelopeV0:
    assert file_path.is_file(), f"Missing webhook JSON file at {file_path}"
    with file_path.open() as f:
        webhook_dict = json.loads(f.read())
        return WebhookEnvelopeV0.from_dict(webhook_dict)
