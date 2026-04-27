import requests
import logging
import json

# get API call
def get_info(url, **kwargs):
    try:
        response = requests.get(url,timeout=10,**kwargs)
        response.raise_for_status()
        logging.info("API run successfully")
        return response.json()

    except requests.exceptions.ConnectionError as e:
        logging.error(f"Connection Error {e}")
    except requests.exceptions.Timeout as e:
        logging.error(f"Timeout Error {e}")
    except json.JSONDecodeError as e:
        logging.error(f"JSONDecodeError {e}")
    except (KeyError,TypeError,ValueError, AttributeError) as e:
        logging.error(e)
    except requests.exceptions.RequestException as e:
        logging.error(f"Other Generic error {e}")
    return None
