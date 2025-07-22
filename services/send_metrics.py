# send_metrics.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://theslow.net/api/slowstats/ingest-metrics"
API_KEY = os.getenv("SLOWSTATS_COMMANDER_API_KEY")
PROJECT_ID = os.getenv("SLOWSTATS_COMMANDER_PROJECT_ID")

if not API_KEY:
    raise EnvironmentError("Missing SLOWSTATS_COMMANDER_API_KEY in .env.")
if not PROJECT_ID:
    raise EnvironmentError("Missing SLOWSTATS_COMMANDER_PROJECT_ID in .env.")

def send_metrics(metrics: dict):
    """
    Sends a batch of metrics to SlowStats using the /ingest-metrics endpoint.
    Each key in `metrics` is a metric name and its value is a number.
    """
    if not isinstance(metrics, dict):
        raise TypeError("metrics must be a dict of {metric_name: float}")

    payload = {
        "projectId": PROJECT_ID,
        "payload": metrics
    }

    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": API_KEY
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=5)
        response.raise_for_status()
        print(f"✅ Sent metrics: {list(metrics.keys())}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send metrics: {e}")
