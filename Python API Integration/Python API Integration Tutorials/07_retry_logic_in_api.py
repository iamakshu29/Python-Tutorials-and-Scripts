# 7_retry_logic_in_api.py — Retry with Exponential Backoff

import requests
import logging
import time

# =============================================
# RETRY CONFIGURATION
# =============================================
# Only retry on transient errors — codes that may resolve on their own.
# 429 = rate limited  |  500/502/503 = server-side temporary failures
# 403 is intentionally excluded — retrying a forbidden request won't help, you need a new key.
MAX_RETRIES = 3

# =============================================
# GET WITH RETRY + EXPONENTIAL BACKOFF
# =============================================
# On a retryable status code, wait grows as 2^attempt: 1s → 2s → 4s.
# This reduces load on a struggling server instead of hammering it immediately.
def get_info(url,**kwargs):
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url,timeout=10,**kwargs)

            if response.status_code in (429,500,502,503):
                wait = 2 ** attempt  # exponential backoff: 1s, 2s, 4s
                logging.warning(f"Retryable status {response.status_code} — retrying in {wait}s (attempt {attempt+1}/{MAX_RETRIES})")
                time.sleep(wait)
                continue  # go to next iteration without returning

            response.raise_for_status()  # raises HTTPError for any other 4xx/5xx not in retry list
            return response.json()

        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            return None  # non-retryable network error — bail immediately

    return None  # all retries exhausted