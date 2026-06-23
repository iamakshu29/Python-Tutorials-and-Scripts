# Module 03 — HTTPX

## Before you start — you must be comfortable with:

  - The requests library basics                                 (01_requests_intro.py)
  - Authentication patterns (API keys, Bearer tokens, OAuth)   (02_01_authentication.py)
  - Retry logic and error handling                             (07_retry_logic_in_api.py)
  - asyncio core: gather, create_task, event loop              (Module 01)
  - asyncio Semaphore for rate limiting                        (Module 02)

  You should have a solid grip on how requests works because httpx mirrors its API.
  The async parts are where it diverges — that's what this module is about.

---

## What this module covers

  httpx is the modern HTTP client for Python — it does both sync AND async.
  This module bridges your existing requests knowledge to the async world.
  After this, you'll never need requests for async code again.

---

## Installation and Usage

  pip install httpx

  import httpx

---

## Concepts to Master

  1. httpx.Client (sync) — the requests replacement
       - httpx.get(), httpx.post() are convenience functions (like requests.get)
       - But the REAL way: use httpx.Client() as a context manager
         with httpx.Client() as client: client.get(...)
       - Why context manager? It handles connection pooling and cleanup
       - Compare: httpx.Response vs requests.Response — very similar API
       - Key addition: response.raise_for_status() raises on 4xx/5xx (same as requests)

  2. httpx.AsyncClient — the async HTTP client
       - async with httpx.AsyncClient() as client: await client.get(...)
       - Always use async with — never instantiate without it
       - All methods are coroutines: await client.get(), await client.post(), etc.
       - Connection pooling: the client reuses TCP connections — HUGE performance gain
       - One client for the lifetime of your app, not one per request

  3. Timeouts
       - httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=5.0)
       - Or just httpx.Timeout(10.0) for a single value across all phases
       - Pass to client: httpx.AsyncClient(timeout=httpx.Timeout(10.0))
       - What each phase means: connect, send, receive, pool acquire
       - Raises httpx.TimeoutException — know how to catch it

  4. Making concurrent requests (this is where it gets real)
       - Use asyncio.gather with multiple await client.get() calls
       - Compare: 10 sequential requests vs 10 concurrent — see the time difference
       - This is the main reason to use async HTTP — true concurrent I/O

  5. Authentication
       - httpx.BasicAuth("user", "pass")
       - httpx.BearerAuth("token") — this is NEW, requests doesn't have this built-in
       - Custom auth: subclass httpx.Auth and implement auth_flow()
       - Attach to client: httpx.AsyncClient(auth=my_auth)

  6. Headers, params, JSON
       - client.get(url, headers={}, params={})
       - client.post(url, json={}) — auto-sets Content-Type: application/json
       - client.post(url, data={}) — form data
       - response.json(), response.text, response.content

  7. Streaming responses
       - For large responses (files, logs, event streams) — don't load all into memory
       - async with client.stream("GET", url) as response:
             async for chunk in response.aiter_bytes(): ...
       - Understand: normal .get() loads the full body; stream() doesn't

  8. Error handling
       - httpx.HTTPStatusError — raised by raise_for_status()
       - httpx.RequestError — network-level errors (connection refused, timeout, etc.)
       - httpx.TimeoutException — specifically for timeouts
       - Know the hierarchy: RequestError is the parent of most errors

  9. Retry logic with httpx
       - httpx does NOT have built-in retry (unlike requests + urllib3)
       - You write retry yourself (you already did this in 07_retry_logic_in_api.py)
       - Now do it async: write an async retry decorator using asyncio
       - Or use the tenacity library: pip install tenacity (supports async)

---

## Things to experiment with (break stuff on purpose)

  - Make a request to a non-existent URL — what exception do you get?
  - Set a very short timeout (0.001s) — watch it fail
  - Make 20 requests with gather — measure vs sequential
  - Make a request WITHOUT async with (don't close the client) — check for resource warnings
  - Try streaming a large file — print chunk sizes to see how data arrives

  Good free APIs to practice with (no auth needed):
    https://httpbin.org/get          — echoes your request back
    https://httpbin.org/delay/2      — delays response by 2 seconds (great for concurrency demos)
    https://httpbin.org/status/500   — returns HTTP 500
    https://jsonplaceholder.typicode.com/posts  — fake REST API
    https://api.github.com/users/python         — GitHub public API

---

## Key mental model

  One AsyncClient = one connection pool.
  The pool keeps TCP connections alive and reuses them.
  Making 100 requests with one client is MUCH faster than creating 100 clients.
  Create the client ONCE (e.g., at app startup), reuse it everywhere.

  httpx.AsyncClient is to asyncio what requests.Session is to sync code —
  except httpx.AsyncClient is even better because it manages the pool automatically.

---

## Vocabulary you must know cold

  connection pool     — a set of reusable TCP connections; avoids reconnect overhead
  TLS handshake       — the SSL setup cost on each NEW connection (pools avoid this)
  streaming           — processing response data in chunks without loading all into memory
  HTTP/2              — httpx supports it; allows multiple requests over ONE connection
  raise_for_status    — method that converts 4xx/5xx into exceptions

---

## Mini Project — Multi-Endpoint Health Checker

  Build an async service that checks the health of multiple API endpoints concurrently.

  Requirements:
    - A list of at least 8 URLs to check (mix of httpbin.org paths, some that will fail)
    - Check all endpoints CONCURRENTLY using AsyncClient + gather
    - For each endpoint record: url, status_code, response_time_ms, is_healthy (bool)
    - An endpoint is "healthy" if it responds within 3 seconds with status < 400
    - Print a summary table at the end: URL | Status | Response Time | Health
    - Handle all error cases: timeout, connection error, non-200 status
    - Limit to max 5 concurrent requests at a time (use Semaphore from Module 02)

  Stretch goals:
    - Run the health check every 30 seconds in a loop (asyncio loop + asyncio.sleep)
    - If an endpoint fails 3 checks in a row, mark it as "CRITICAL" and print an alert
    - Retry failed endpoints once before marking as unhealthy
    - Add response headers to the output (e.g., content-type, server)
    - Write results to a JSON file after each check run

  File to create: 03_httpx/health_checker.py

---

## You're ready for Module 04 when:

  - You can write async HTTP calls with proper error handling without looking up the API
  - You know why to reuse AsyncClient instead of creating per request
  - You've actually seen the speedup from concurrent requests vs sequential
  - You've implemented retry logic for async HTTP calls
  - Your health checker correctly limits concurrency with a Semaphore
