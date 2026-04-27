#  Send a POST request with a JSON body and handle 4xx/5xx retries.

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

url = "https://postman-echo.com/post"

payload = {
    "name": "John Doe",
    "job": "DevOps"
}

# Configure retry strategy
retry_strategy = Retry(
    total=5,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["POST"],
    backoff_factor=1,
    raise_on_status=False
)

adapter = HTTPAdapter(max_retries=retry_strategy)

session = requests.Session()
session.mount("https://", adapter)
session.mount("http://", adapter)

response = session.post(url, json=payload)

# Explicit error handling
if response.status_code >= 400:
    raise requests.HTTPError(
        f"Request failed: {response.status_code}, body={response.text}"
    )

data = response.json()
print(data)
# print(response.status_code)
