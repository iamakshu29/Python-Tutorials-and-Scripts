## 1. Service Health Check Script

# Expectation
# - Call a health endpoint of a service
# - Detect healthy vs unhealthy states
# - Handle network failures
# - Exit with appropriate status

import requests

url = "https://httpbin.org"
# url = "https://httpbin.org/uaiu"

try: 
    res = requests.get(url, timeout=5)
    if res.status_code == 200:
        print("service is healthy")
    else:
        print(f"Service not healthy, status code is {res.status_code}")
except requests.exceptions.RequestException as e:
    print(f"Health check failed: {e}")

# Use case
# - Used in cron jobs, CI pipelines, or readiness checks.
# - Interview angle: retries, timeouts, status handling.