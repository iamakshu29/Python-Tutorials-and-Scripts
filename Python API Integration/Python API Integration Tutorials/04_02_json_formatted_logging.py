import logging
import json
import os
from datetime import datetime, UTC

# Setup basic logging
def configure_logging(log_file):
    try:
        os.makedirs(os.path.dirname(log_file),exist_ok=True)
        logging.basicConfig(
            filename = log_file,
            level = logging.INFO,
            format = "%(asctime)s - %(levelname)s - %(message)s"
        )
    except Exception as e:
        return e

def log_event(level, event, **fields):
    logging.log(
        level,
        json.dumps({
            "timestamp": datetime.now(UTC).isoformat(),
            "event": event,
            **fields
        })
    )

configure_logging("./logging_json_demo_app.log")

def div():
    try:
        ans = 1/0
        return ans
    except ZeroDivisionError as e:
        log_event(logging.ERROR,"Denominator can't be 0")
        return None
div()