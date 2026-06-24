# 02_things_to_experiment.py — httpx Experiments: Break Things on Purpose

# =============================================
# EXP 1: Non-Existent URL / Short Timeout / 20 Concurrent Requests
# =============================================
# Three experiments in one main():
#   1. Request to a non-existent domain — what exception fires?
#   2. Timeout set to 0.001s — forces an immediate TimeoutException
#   3. 20 requests sequential vs concurrent — measure the time difference

import httpx
import asyncio
import json
import time


async def fetch_url(client, url, timeout):
    try:
        response = await client.get(url, timeout=timeout)
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


async def main():
    URLs = {
        "non_existent_url": "https://non_existent_url.com/",
        "reduce_timeout": "https://pokeapi.co/api/v2/pokemon/charizard",
        "multi_request": "https://pokeapi.co/api/v2/pokemon/charizard",
    }
    timeout = httpx.Timeout(0.001)  # Intentionally tiny — will trigger TimeoutException
    results = {}

    async with httpx.AsyncClient() as client:
        result_1 = await fetch_url(client, URLs["non_existent_url"], timeout=3.0)  # ConnectError expected
        results["result_1"] = result_1

    async with httpx.AsyncClient() as client:
        result_2 = await fetch_url(client, URLs["reduce_timeout"], timeout)  # TimeoutException expected
        results["result_2"] = result_2

    async with httpx.AsyncClient() as client:
        # Sequential — each request waits for the previous to finish
        start_time_seq = time.perf_counter()
        for _ in range(20):
            await fetch_url(client, URLs["multi_request"], timeout=3.0)
        end_time_seq = time.perf_counter()

        # Concurrent — all 20 requests fire at the same time
        start_time_conc = time.perf_counter()
        tasks = [
            fetch_url(client, URLs["multi_request"], timeout=3.0) for _ in range(20)
        ]
        await asyncio.gather(*tasks)
        end_time_conc = time.perf_counter()

        results["sequential_time_sec"] = round(end_time_seq - start_time_seq, 2)
        results["concurrent_time_sec"] = round(end_time_conc - start_time_conc, 2)

    return results


# data = asyncio.run(main())
# print(json.dumps(data, indent=2))


# =============================================
# EXP 2: AsyncClient Without Context Manager
# =============================================
# If you create AsyncClient without async with and never call aclose(),
# Python emits a ResourceWarning about an unclosed socket.
# Fix: always use async with, or call await client.aclose() in a finally block.
import warnings

warnings.simplefilter("always", ResourceWarning)


async def main():
    client = httpx.AsyncClient()  # Intentionally not used as a context manager

    response = await client.get("https://pokeapi.co/api/v2/pokemon/charizard")
    print(response.status_code)

    # await client.aclose()  # Commenting this out triggers the ResourceWarning


# asyncio.run(main())


# =============================================
# EXP 3: Streaming a Large File
# =============================================
# stream() opens the connection without loading the full body.
# aiter_bytes(chunk_size=N) yields chunks of up to N bytes as they arrive.
# Useful for large downloads, log tailing, or server-sent events.
async def fetch_stream_data(url):
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", url) as response:
            response.raise_for_status()

            total = 0

            async for chunk in response.aiter_bytes(chunk_size=50000):
                if chunk:
                    chunk_len = len(chunk)
                    total += chunk_len
                    print(f"Received chunk: {chunk_len} bytes")
                    # print(chunk[:50])

            print(f"Total received: {total} bytes")


async def main():
    pokemon_url = "https://pokeapi.co/api/v2/pokemon/charizard"

    await fetch_stream_data(pokemon_url)


# asyncio.run(main())
