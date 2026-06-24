# 01_learning_httpx.py — httpx: Sync and Async HTTP Client

# =============================================
# SETUP — Imports and Environment
# =============================================
# httpx mirrors the requests API but supports async natively.
# Load API credentials from .env in the same folder as this file.
import requests
import httpx
import asyncio
import json
import os
import time
from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_PATH)
API_KEY = os.getenv("OPENWEATHER_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
URL = "https://api.github.com/user"

# requests equivalent — shown for comparison only
# response = requests.get(URL, headers=headers)
# print(response.json())


# =============================================
# 1. httpx.Client (Sync) — The requests Replacement
# =============================================
# httpx.Client() is the sync equivalent of requests.Session().
# Always use it as a context manager — handles connection pooling and cleanup automatically.
# response.raise_for_status() raises httpx.HTTPStatusError on 4xx/5xx (same as requests).
# with httpx.Client() as client:
#     try:
#         response = client.get(URL, headers=headers)
#         response.raise_for_status()
#         print(response.json())
#     except httpx.HTTPStatusError as e:
#         print(f"HTTP Error: {e.response.status_code}")
#         print(e.response.text)

#     except httpx.RequestError as e:
#         print(f"Request failed: {e}")

#     except Exception as e:
#         print(f"Unexpected error: {e}")


# =============================================
# 2. httpx.AsyncClient — The Async HTTP Client
# =============================================
# Always use async with — never instantiate without the context manager.
# All request methods are coroutines: await client.get(), await client.post(), etc.
# One-off usage: create the client inside the async function, close on exit. if using as client = httpx.AsyncClient()
async def fetch(URL1, headers):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(URL, headers=headers)
            response.raise_for_status()
            print(response.json())
        except httpx.HTTPStatusError as e:
            print(f"HTTP Error: {e.response.status_code}")
            print(e.response.text)

        except httpx.RequestError as e:
            print(f"Request failed: {e}")

        except Exception as e:
            print(f"Unexpected error: {e}")


async def main():
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

    await fetch(URL, headers)


# asyncio.run(main())


# =============================================
# NOTE: Connection Pooling vs Concurrency
# =============================================
# Connection pooling (single shared client) = moderate speed gain — reuses TCP/TLS sockets.
# Async concurrency (gather/create_task) = the major speed gain — all I/O runs in parallel.
# The code below demonstrates pooling WITHOUT concurrency — requests still run sequentially.
# To get both benefits: share one AsyncClient AND use gather().


async def fetch(client, url, headers):
    try:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.status_code

    except httpx.HTTPStatusError as e:
        print(f"HTTP Error: {e.response.status_code}")
        print(e.response.text)

    except httpx.RequestError as e:
        print(f"Request failed: {e}")

    except Exception as e:
        print(f"Unexpected error: {e}")


async def main():
    client = httpx.AsyncClient()
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    URLs = [
        "https://api.github.com/user",
        "https://api.github.com/users/octocat",
        "https://api.github.com/repos/octocat/Hello-World",
    ]
    results = []
    try:
        for url in URLs:
            results.append(await fetch(client, url, headers))
    finally:
        await client.aclose()
    return results


# print(asyncio.run(main()))


# =============================================
# 3. Timeouts
# =============================================
# httpx.Timeout lets you set independent deadlines for each phase of a request.
# httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=5.0)
# connect=5.0  → max time to establish a TCP connection (raises ConnectTimeout if exceeded)
# write=10.0   → max time to send request data (relevant for large POST/PUT uploads)
# read=30.0    → max time waiting for response data (applies to all methods, not just GET)
# pool=5.0     → max time waiting for a free connection from the pool (raises PoolTimeout)
# httpx.Timeout(10.0) → single value applied to all four phases
# Exception to catch: httpx.TimeoutException (parent of all timeout errors)


async def fetch(client, url, timeout):
    try:
        response = await client.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()

    except httpx.HTTPStatusError as e:
        print(f"HTTP Error: {e.response.status_code}")
        print(e.response.text)

    except httpx.TimeoutException as e:
        print(f"Exception Type: {type(e).__name__}")

    except httpx.RequestError as e:
        print(f"Request failed: {e}")

    except Exception as e:
        print(f"Unexpected error: {e}")


async def main():
    URL = "https://api.github.com/users/octocat"
    timeout = httpx.Timeout(
        connect=5.0, read=30.0, write=10.0, pool=5.0
    )  # Try setting connect or read to 0 to force a timeout error

    async with httpx.AsyncClient() as client:
        result = await fetch(client, URL, timeout=timeout)
        return result


# print(asyncio.run(main()))


# =============================================
# 4. Making Concurrent Requests
# =============================================
# asyncio.gather() fires all requests at the same time — total time ≈ slowest single request.
# Compare: sequential (N * avg latency) vs concurrent (max latency) — dramatic difference.
# RULE: always share ONE AsyncClient across all concurrent requests — enables connection reuse.


async def fetch_github_data(client, url, headers):

    response = await client.get(url, headers=headers)

    # return response.json()
    return response


async def test_connection_pooling_without_concurrency(URLs, headers):
    responses = []

    async with httpx.AsyncClient() as client:
        for url in URLs:
            responses.append(await fetch_github_data(client, url, headers))

        return responses


async def test_connection_pooling_with_concurrency(URLs, headers):
    async with httpx.AsyncClient() as client:
        tasks = [fetch_github_data(client, url, headers) for url in URLs]
        responses = await asyncio.gather(*tasks)
        return responses


async def main():
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    URLs = [
        "https://api.github.com/user",
        "https://api.github.com/users/octocat",
        "https://api.github.com/repos/octocat/Hello-World",
    ]

    result = []
    start = time.perf_counter()
    result.append(await test_connection_pooling_without_concurrency(URLs, headers))
    end = time.perf_counter()
    print(f"Total Time without Concurrency - {end - start} \n\n")

    start = time.perf_counter()
    result.append(await test_connection_pooling_with_concurrency(URLs, headers))
    end = time.perf_counter()
    print(f"Total Time with Concurrency - {end - start} \n\n")

    return result


# print(asyncio.run(main()))


# =============================================
# 5. Authentication
# =============================================
# httpx has built-in auth helpers — attach per request or for the entire client session.
# httpx.BasicAuth("user", "pass")   → Base64-encodes credentials in Authorization header
# httpx.BearerAuth("token")         → sets Authorization: Bearer <token> (no requests equivalent)
# Custom auth: subclass httpx.Auth and implement auth_flow() for complex flows (OAuth, HMAC)
#
# Per request:  client.get(url, auth=auth)
# Per session:  httpx.AsyncClient(auth=auth)  → applied to every request from that client
#
# BasicAuth sync example (commented out — uncomment to test):
# auth = httpx.BasicAuth(username="finley", password="secret")
# client = httpx.Client(auth=auth)
# try:
#     response = client.get("https://httpbin.org/basic-auth/finley/secret")
#     print(response.text)
# except Exception as e:
#     print(f"{e}")


# =============================================
# 6 & 8. Headers, Params, JSON and Error Handling
# =============================================
# Request building — same as requests:
#   client.get(url, headers={}, params={})   → query string appended automatically
#   client.post(url, json={})               → auto-sets Content-Type: application/json
#   client.post(url, data={})               → form-encoded body
#   response.json() / response.text / response.content
#
# Error hierarchy (catch in this order — most specific first):
#   httpx.HTTPStatusError   → raised by raise_for_status() on 4xx/5xx
#   httpx.TimeoutException  → any timeout phase (connect, read, write, pool)
#   httpx.RequestError      → network-level errors (DNS, connection refused) — parent of TimeoutException
#   Exception               → catch-all for unexpected errors
#
# NOTE: We are already using headers above (Bearer token) and error handling in every fetch() above.
####   This section consolidates the reference for both topics.


# =============================================
# 7. Streaming Responses
# =============================================
# For large responses (files, logs, event streams) — stream instead of loading all into memory.
# client.stream() returns an async context manager; aiter_bytes() yields chunks as they arrive.
# Normal .get() loads the full body before returning — use stream() for anything large.
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            async for chunk in response.aiter_bytes(chunk_size=256):
                if chunk:
                    print(chunk)


async def main():
    pokemon_url = "https://pokeapi.co/api/v2/pokemon/charizard"

    await fetch_stream_data(pokemon_url)


# asyncio.run(main())


# =============================================
# 9. Retry Logic
# =============================================
# httpx has no built-in retry (unlike requests + urllib3's Retry adapter).
# Write retry manually: loop with exponential backoff on TimeoutException.
# 2**attempt gives delays of 1s, 2s, 4s ... between retries.
# For production use, consider the tenacity library (supports async natively).
async def fetch_request_with_retry_logic(url):
    async with httpx.AsyncClient() as client:
        for attempt in range(3):
            try:
                return await client.get(url, timeout=10)
            except httpx.TimeoutException:
                if attempt == 2:
                    raise
                await asyncio.sleep(2**attempt)


async def main():
    url = "https://api.github.com/users/python"

    result = await fetch_request_with_retry_logic(url)
    return result.json()


# print(asyncio.run(main()))
