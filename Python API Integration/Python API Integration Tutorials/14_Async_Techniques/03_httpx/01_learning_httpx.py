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

### using requests module just as an example.
# response = requests.get(URL, headers=headers)
# print(response.json())

## 1. httpx.Client (sync) — the requests replacement
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


# 2. httpx.AsyncClient — the async HTTP client
# context manager should always be inside an async function
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


# 2. last line - One client for the lifetime of your app, not one per request
# so insted of calling the fetch() which close every connection after use,
# we create AsyncClient connection and will use for the lifetime of app, not one per request and close the connection at the end.


# ALSO, The below code is just showing connection pooling not Concurrency
# It uses a single client which makes it a little fast as it avoids repeatedly creating TCP/TLS connections.
# but without create_task or gather it still executing sequentially not "concurrently" -> which leads to huge gain in speed

# Connection pooling = moderate performance improvement by reusing sockets.
# Async concurrency (gather) = often the major performance improvement when making multiple independent requests.


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


# 3. Timeouts
## httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=5.0)

# connect=5.0 -> Maximum time allowed to establish a TCP connection.
### If the server is unreachable or slow to accept connections, httpx.ConnectTimeout is raised.
# write=10.0 -> Maximum time allowed to send request data to the server. Relevant for POST,PUT,PATCH requests
### especially when uploading large files.
# read=30.0 -> Maximum time allowed while waiting for response data.
###  read timeout applies whenever the client is waiting for response data, regardless of GET, POST, PUT, PATCH, DELETE, etc.
# pool=5.0 -> If a request wait for a free connection longer than the pool timeout then httpx.PoolTimeout is raised
### can be due to rate limiter
# httpx.Timeout(10.0) -> single value across all phases
# raised exception to catch -> httpx.TimeoutException


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
    )  # Try to play with connect and read, make them 0 and check

    async with httpx.AsyncClient() as client:
        result = await fetch(client, URL, timeout=timeout)
        return result


# print(asyncio.run(main()))


# 4. Making concurrent requests (this is where it gets real)


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


# 5. Authentication
# - auth = httpx.BasicAuth("user", "pass")
# Either use it per request or per session
### Per Request
# client = httpx.Client()
# response = client.get("https://www.example.com/", auth=auth)
### Per Session
# client = httpx.Client(auth=auth)
# response = client.get("https://www.example.com/")

# BasicAuth Example in Sync request
# auth = httpx.BasicAuth(username="finley", password="secret")
# client = httpx.Client(auth=auth)
# try:
#     response = client.get("https://httpbin.org/basic-auth/finley/secret")
#     print(response.text)
# except Exception as e:
#     print(f"{e}")


#   6. Headers, params, JSON and
#        - client.get(url, headers={}, params={})
#        - client.post(url, json={}) — auto-sets Content-Type: application/json
#        - client.post(url, data={}) — form data
#        - response.json(), response.text, response.content
# AND
#   8. Error handling
#        - httpx.HTTPStatusError — raised by raise_for_status()
#        - httpx.RequestError — network-level errors (connection refused, timeout, etc.)
#        - httpx.TimeoutException — specifically for timeouts
####     - Know the hierarchy: RequestError is the parent of most errors
## its basic we already using headers above for providing Bearer Token for github api, response objects and error handling as well.


# 7. Streaming responses
async def fetch_stream_data(url):
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


# 9. Retry Logic
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
