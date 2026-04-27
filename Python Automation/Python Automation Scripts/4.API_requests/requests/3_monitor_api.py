import time
import requests
from datetime import datetime,timezone

API_URL = "https://example.com/health"
WEBHOOK_URL = "https://webhook.site/your-webhook-id"
INTERVAL_SECONDS = 5
TIMEOUT_SECONDS = 3

last_status = None

def check_api():
    try:
        response = requests.get(API_URL, timeout=TIMEOUT_SECONDS)
        return response.status_code
    except requests.RequestException:
        # Treat network errors as a distinct status
        return "ERROR"

def trigger_webhook(old_status, new_status):
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "api_url": API_URL,
        "previous_status": old_status,
        "current_status": new_status
    }

    requests.post(WEBHOOK_URL, json=payload, timeout=TIMEOUT_SECONDS)

while True:
    current_status = check_api()

    if current_status != last_status:
        if last_status is not None:
            trigger_webhook(last_status, current_status)
        last_status = current_status

    time.sleep(INTERVAL_SECONDS)
