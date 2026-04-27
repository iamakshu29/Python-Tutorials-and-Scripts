import requests
import logging
import time
from json import JSONDecodeError
from log_utils.logger import log_event

MAX_RETRIES = 3
# (429,500,502,503) -> A 403 is not in that list (and shouldn't be — retrying a forbidden request won't help, you need a new key)
def get_info(method,url,**kwargs):
    for attempt in range(MAX_RETRIES):     
        try:
            response = requests.request(method,url,timeout=10,**kwargs)
            if response.status_code in (429,500,502,503):
                wait = 2 ** attempt
                log_event(logging.WARNING, "retrying", status=response.status_code, wait=wait)
                time.sleep(wait)
                continue
            response.raise_for_status()
            if method == "GET":
                log_event(logging.INFO,"GET API Execute Successfully")
                return response.json()
            if method == "POST":
                log_event(logging.INFO,"POST API Execute Successfully")
                return response.json()
            if method == "PUT":
                log_event(logging.INFO,"PUT API Execute Successfully")
                return response.json()
            
        except requests.exceptions.ConnectionError as e:
            log_event(logging.ERROR,"Connection Error",error_type=type(e).__name__,error_message=str(e),url=url)
            logging.error(f"Connection Error {e}")
        except requests.exceptions.Timeout as e:
            log_event(logging.ERROR,"request_timeout",error_type=type(e).__name__,error_message=str(e),url=url)
        except JSONDecodeError as e:
            log_event(logging.ERROR,"JSONDecodeError",error_type=type(e).__name__,error_message=str(e),url=url)
        except (KeyError,TypeError,ValueError, AttributeError) as e:
            log_event(logging.ERROR,"handled_exception",error_type=type(e).__name__,error_message=str(e),url=url)
        except requests.exceptions.RequestException as e:
            log_event(logging.ERROR,"request_exception",error_message=str(e),url=url)
            return None
    return None



