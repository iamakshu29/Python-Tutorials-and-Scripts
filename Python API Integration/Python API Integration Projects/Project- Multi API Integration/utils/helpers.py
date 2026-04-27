import logging
import os

# convert temp to celsius
def kelvin_to_celsius(k):
    return round(k - 273.15, 2)

# add insight based on temp.
def generate_insight(temp):
    if temp > 35:
        return "High temperature, consider indoor work"
    elif temp < 15:
        return "Cool weather, productive coding environment"
    else:
        return "Moderate weather, good for coding"

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