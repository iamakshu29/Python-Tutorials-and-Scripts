# 04_template.py — httpx AsyncClient Reusable Template

# =============================================
# PATTERN OVERVIEW
# =============================================
# Keep the request function focused on ONE URL — no looping inside it.
# All iteration, gathering, and orchestration belongs in main().
# This makes the fetch function reusable for any single URL or batched calls.
#
# Two ways to manage AsyncClient lifetime:
#   Without context manager — manual aclose() in finally (verbose but explicit)
#   With context manager   — preferred; auto-closes even on exceptions

import httpx
import asyncio


# =============================================
# FETCH FUNCTION — Single Request (Reusable)
# =============================================
# Takes a shared client and a single URL — no loops, no orchestration.
# Called once per URL from main(); gather() handles concurrency.
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


# =============================================
# WITHOUT CONTEXT MANAGER — Manual Cleanup
# =============================================
# Client must be explicitly closed via aclose() in a finally block.
# Useful when the client needs to outlive a single async with block.
async def main_without_context_manager_httpx_asyncclient():
    client = httpx.AsyncClient()
    URLs = [f"https://pokeapi.co/api/v2/evolution-chain/{i}" for i in range(1, 9)]

    try:
        tasks = [fetch_url(client, url) for url in URLs]  # Build task list
        return await asyncio.gather(*tasks)               # Fire all concurrently

    finally:
        await client.aclose()  # Always close, even if gather() raises


# =============================================
# WITH CONTEXT MANAGER — Preferred Pattern
# =============================================
# async with ensures aclose() is called automatically on exit, success or exception.
async def main_with_context_manager_httpx_asyncclient():
    URLs = [f"https://pokeapi.co/api/v2/evolution-chain/{i}" for i in range(1, 9)]

    async with httpx.AsyncClient() as client:             # Auto-closes on block exit
        tasks = [fetch_url(client, url) for url in URLs]
        return await asyncio.gather(*tasks)


print("Without Context Manager")
print(asyncio.run(main_without_context_manager_httpx_asyncclient()))
print("\n")
print("With Context Manager")
print(asyncio.run(main_with_context_manager_httpx_asyncclient()))
