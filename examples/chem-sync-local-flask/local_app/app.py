from threading import Thread

from benchling_sdk.apps.helpers.webhook_helpers import verify_app_installation
from flask import Flask, request

from local_app.handler import handle_webhook

app = Flask("benchling-app")


@app.route("/health")
def health_check():
    # Just a route allowing us to check that Flask itself is up and running
    return "OK", 200


@app.route("/1/webhooks/<path:target>", methods=["POST"])
def receive_webhooks(target: str):
    # For security, don't do anything else without first verifying the webhook
    app_id = request.json["app"]["id"]  # type: ignore[index]
    verify_app_installation(app_id, request.data.decode("utf-8"), request.headers)
    app.logger.debug("Received webhook message: %s", request.json)
    # Dispatch work to a thread and ACK webhook as quickly as possible
    thread = Thread(
        target=handle_webhook,
        args=(request.json,)
    )
    thread.start()
    # ACK webhook by returning 2xx status code so Benchling knows the app received the signal
    return "OK", 200
