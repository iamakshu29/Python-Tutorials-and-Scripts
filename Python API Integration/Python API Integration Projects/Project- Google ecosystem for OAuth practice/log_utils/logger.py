import logging
import json
import os
from datetime import datetime

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
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event": event,
            **fields
        })
    )