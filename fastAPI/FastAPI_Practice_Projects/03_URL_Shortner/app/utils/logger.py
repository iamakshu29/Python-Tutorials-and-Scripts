import logging
from datetime import datetime, UTC
import json


def config_logging(log_file):
    try:
        logging.basicConfig(
            filename=log_file, level=logging.INFO, format="%(levelname)s - %(message)s"
        )
    except Exception as e:
        return e


def log_event(level, event, **fields):
    logging.log(
        level,
        json.dumps(
            {"timestamp": datetime.now(UTC).isoformat(), "detail": event, **fields}
        ),
    )


# log_event(logging.ERROR,"Denominator can't be 0")
