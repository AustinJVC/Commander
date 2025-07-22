import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_URL = "https://theslow.net/api/slowstats/ingest-events"
API_KEY = os.getenv("SLOWSTATS_COMMANDER_API_KEY")
PROJECT_ID = os.getenv("SLOWSTATS_COMMANDER_PROJECT_ID")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

if not API_KEY:
    raise EnvironmentError("Missing SLOWSTATS_API_KEY in .env.")
if not PROJECT_ID:
    raise EnvironmentError("Missing SLOWSTATS_PROJECT_ID in .env.")

def send_event(
    event_type: str,
    description: str = None,
    payload: dict = None,
    color: int = None,
    webhook_title: str = None,
    webhook_description: str = None,
):
    if not event_type:
        raise ValueError("event_type is required.")

    # Construct payload
    data = {
        "projectId": PROJECT_ID,
        "eventType": event_type
    }
    if description:
        data["description"] = description
    if payload:
        data["payload"] = payload
    if color is not None:
        data["color"] = color

    # Optional Discord webhook
    if DISCORD_WEBHOOK_URL:
        discord_webhook = {
            "url": DISCORD_WEBHOOK_URL,
            "title": _sanitize_discord_text(webhook_title or "New event triggered"),
        }
        if webhook_description:
            discord_webhook["description"] = _sanitize_discord_text(webhook_description)
        data["discordWebhook"] = discord_webhook

    # Prepare headers
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }

    # Send request
    try:
        response = requests.post(API_URL, json=data, headers=headers, timeout=5)
        response.raise_for_status()
        print("✅ Event sent successfully.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send event: {e}")

def _sanitize_discord_text(text: str) -> str:
    """Redacts mentions and basic PII from webhook titles/descriptions."""
    return (
        text.replace("@", "[redacted]")
            .replace("#", "[redacted]")
            .replace("server", "[redacted]")
            .replace("guild", "[redacted]")
    )
