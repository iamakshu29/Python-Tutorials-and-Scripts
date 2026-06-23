"""
Build an async service that checks the health of multiple API endpoints concurrently.

Requirements:
  - A list of at least 8 URLs to check (mix of httpbin.org paths, some that will fail) - done
  - Check all endpoints CONCURRENTLY using AsyncClient + gather - done
  - For each endpoint record: url, status_code, response_time_ms, is_healthy (bool) - done except errors creating
  - An endpoint is "healthy" if it responds within 3 seconds with status < 400 - done
  - Print a summary table at the end: URL | Status | Response Time | Health - done used list of dict instead
  - Handle all error cases: timeout, connection error, non-200 status - done
  - Limit to max 5 concurrent requests at a time (use Semaphore from Module 02) - done (See the response time after 5th request decrease drastically)

Stretch goals:
  - Run the health check every 30 seconds in a loop (asyncio loop + asyncio.sleep)
  - If an endpoint fails 3 checks in a row, mark it as "CRITICAL" and print an alert
  - Retry failed endpoints once before marking as unhealthy
  - Add response headers to the output (e.g., content-type, server)
  - Write results to a JSON file after each check run

File to create: 03_httpx/health_checker.py
"""

import httpx
import asyncio
import json


async def check_api_health(client, url, response_threshold_ms, timeout, sem):
    async with sem:
        start = asyncio.get_running_loop().time()
        try:
            result = []
            response = await client.get(url, timeout=timeout)
            elapsed_ms = round(
                (asyncio.get_running_loop().time() - start) * 1000,
                2,
            )
            result.append(
                {
                    "url": str(response.url),
                    "status_code": response.status_code,
                    "response_time_ms": elapsed_ms,
                    "success": elapsed_ms < response_threshold_ms
                    and response.status_code < 400,
                }
            )
            return result

        except httpx.TimeoutException as e:
            print(f"Exception Type: {type(e).__name__}")

        except httpx.RequestError as e:
            print(f"Request failed: {e}")

        except Exception as e:
            print(f"Unexpected error: {e}")


async def main():
    URLs = [f"https://pokeapi.co/api/v2/evolution-chain/{i}" for i in range(1, 9)]
    timeout = httpx.Timeout(3.0)
    response_threshold_ms = 3000
    sem = asyncio.Semaphore(5)

    async with httpx.AsyncClient() as client:
        tasks = [
            check_api_health(client, url, response_threshold_ms, timeout, sem)
            for url in URLs
        ]
        return await asyncio.gather(*tasks)


data = asyncio.run(main())

print(json.dumps(data, indent=2))
