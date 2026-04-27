from api.client import get_info
from log_utils.logger import log_event
import logging
import requests
from datetime import datetime



def send_data(api_key, file_path):
    try:
        url = "https://reqres.in/api/users"
        headers = {
            "x-api-key": api_key
        }
        response = get_info("POST",url,json=file_path,headers=headers)
        if response is not None:
            log_event(logging.INFO,"Write Data Successfully",record_count=len(response),url=url)
            log_event(logging.DEBUG,"post_response",response=response)
        else:
            log_event(logging.WARNING,"post_no_response",url=url)

    except (KeyError, TypeError, ValueError, AttributeError) as e:
        log_event(logging.ERROR,"handled_exception",error_type=type(e).__name__,error_message=str(e))

    except requests.exceptions.RequestException as e:
        log_event(logging.ERROR,"request_exception",error_message=str(e))


"""
First Create api_key by logging to site 
https://app.reqres.in/

the headers key is x-api-key

CURL Command is 
curl -X POST "https://reqres.in/api/users" \
  -H "x-api-key: reqres_df7dxxxxxxxxxxxxxxxxb21742efa74" \
  -H "Content-Type: application/json" \
  -d '{"name":"rahul"}'
"""