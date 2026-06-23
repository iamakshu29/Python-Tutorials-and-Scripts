# give the template with 2 example here
# like how to use httpx.AsyncClient() with and without context manager

# SpeciallyI want to show this

# like with one request it simple
# but with multiple I wan to show that we create the hit url function once and then all the traversing or looping will be done in main func
# i.e. we are not looping inside the main request function instead we are calling the func mutiple times as per requirement from main() with differetn url or params.

import httpx
import asyncio


async def fetch_url(client, url):
    try:
        response = await client.get(url, timeout=3.0)
        response.raise_for_status()
        return response.status_code

    except httpx.HTTPStatusError as e:
        print(f"HTTP Error: {e.response.status_code}")
        print(e.response.text)

    except httpx.TimeoutException as e:
        print(f"Exception Type: {type(e).__name__}")

    except httpx.RequestError as e:
        print(f"Request failed: {e}")

    except Exception as e:
        print(f"Unexpected error: {e}")


async def main_without_context_manager_httpx_asyncclient():
    client = httpx.AsyncClient()
    URLs = [f"https://pokeapi.co/api/v2/evolution-chain/{i}" for i in range(1, 9)]

    try:
        tasks = [fetch_url(client, url) for url in URLs]
        return await asyncio.gather(*tasks)

    finally:
        await client.aclose()


## Preferred
async def main_with_context_manager_httpx_asyncclient():
    URLs = [f"https://pokeapi.co/api/v2/evolution-chain/{i}" for i in range(1, 9)]

    async with httpx.AsyncClient() as client:
        tasks = [fetch_url(client, url) for url in URLs]
        return await asyncio.gather(*tasks)


print("Without Context Manager")
print(asyncio.run(main_without_context_manager_httpx_asyncclient()))
print("\n")
print("With Context Manager")
print(asyncio.run(main_with_context_manager_httpx_asyncclient()))
