# Final Project — Async API Aggregator

## Do this ONLY after all 5 mini projects are done.

  This is not a tutorial. There are no hints on HOW to build it.
  Only WHAT to build and what it must be able to do.
  Every concept from every module should appear somewhere in here.

---

## What you're building

  A command-line async service that aggregates data from multiple public APIs,
  processes it concurrently, stores results, and produces a structured report.

  Think of it as a mini data pipeline — the kind you'd build for a monitoring
  dashboard, a reporting service, or a data aggregation microservice.

---

## The system must do the following

  Data Sources (use all of these — they're free, no auth needed):
    - JSONPlaceholder (https://jsonplaceholder.typicode.com)
      → /users, /posts, /todos, /comments
    - HTTPBin (https://httpbin.org)
      → use /delay/N endpoints to simulate slow external services
    - Open-Meteo Weather API (https://api.open-meteo.com/v1/forecast)
      → fetch current temperature for at least 3 cities (pass lat/lon as params)
    - GitHub API (https://api.github.com)
      → /users/{username}, /users/{username}/repos (use your own or any public account)

  Core requirements:
    1. All HTTP calls must use httpx.AsyncClient (one shared client, not one per request)
    2. Fetch from ALL data sources concurrently — measure total time vs sequential estimate
    3. Max 5 concurrent requests at any time (Semaphore)
    4. Retry failed requests up to 2 times with exponential backoff (1s, 2s)
    5. Circuit breaker: after 3 failures on one host, stop calling it for 60 seconds
    6. All results processed through an async pipeline (async generators)
    7. At least one CPU-bound step (e.g., compute stats, hash data) — run in thread pool
    8. Write results to a JSON report file using aiofiles (stream writes, not all at end)
    9. Graceful shutdown: handle KeyboardInterrupt — cancel all tasks cleanly, flush file

  Report format (JSON file):
    {
      "generated_at": "ISO timestamp",
      "total_duration_seconds": 4.2,
      "sources": {
        "jsonplaceholder": { "users_fetched": 10, "posts_fetched": 100, ... },
        "weather": { "cities": [...] },
        "github": { "repos": [...] }
      },
      "errors": [ { "url": "...", "error": "...", "retries": 2 } ],
      "circuit_breakers": { "httpbin.org": "OPEN — skipped 5 requests" }
    }

---

## Architecture to figure out yourself

  You need to decide:
    - How to structure your async pipeline (producers → transformers → writers)
    - Where to put the circuit breaker logic (class? decorator? module?)
    - How to share the AsyncClient across all fetchers (pass it in? singleton? context manager?)
    - How to coordinate shutdown when Ctrl+C is pressed
    - How to handle partial failures (one source fails — others still complete)

  There is no single correct architecture. Pick one, build it, then ask yourself:
    "If I needed to add a 5th data source, how much would I need to change?"
    If the answer is "a lot", your architecture needs work.

---

## Skills checklist — every item below must appear somewhere in your code

  From Module 01:
    [ ] asyncio.gather or TaskGroup to run coroutines concurrently
    [ ] asyncio.create_task for fire-and-forget background work
    [ ] timing with time.perf_counter to measure actual speedup

  From Module 02:
    [ ] asyncio.Semaphore to limit concurrency
    [ ] asyncio.Queue for a producer-consumer pipeline
    [ ] asyncio.wait_for or asyncio.timeout for request timeouts
    [ ] asyncio.Event for a "ready" signal (e.g., "client initialized" event)

  From Module 03:
    [ ] httpx.AsyncClient as a shared context manager
    [ ] httpx.Timeout with different connect/read values
    [ ] raise_for_status() with proper error handling
    [ ] at least one streaming response (even if just iterating bytes)

  From Module 04:
    [ ] asyncio.to_thread for CPU-bound work (stats computation or hashing)
    [ ] as_completed to process results as they arrive
    [ ] circuit breaker implementation (your own class)
    [ ] rate limiting (Semaphore + token bucket or counter approach)

  From Module 05:
    [ ] @asynccontextmanager for at least one resource
    [ ] async generator pipeline (at minimum: fetch → transform → write)
    [ ] aiofiles for writing the report file
    [ ] proper async cleanup in __aexit__ / finally blocks

---

## What "done" looks like

  - Run it: python aggregator.py
  - It fetches data from all sources concurrently
  - Prints live progress: "Fetched users [OK 0.3s]", "Weather London [OK 0.8s]", etc.
  - Writes report.json incrementally as data arrives
  - If you Ctrl+C midway, it prints "Shutting down..." and exits cleanly
  - report.json contains whatever was fetched before the interrupt
  - All error cases are handled — no unhandled exceptions should crash the process

---

## Suggested folder structure

  FINAL_PROJECT/
    aggregator.py          ← entry point
    fetchers/
      jsonplaceholder.py   ← all JSONPlaceholder fetch logic
      weather.py           ← weather API fetch logic
      github.py            ← GitHub API fetch logic
    pipeline/
      transformers.py      ← async generator transforms
      writers.py           ← aiofiles report writing
    utils/
      circuit_breaker.py   ← CircuitBreaker class
      retry.py             ← async retry logic
      rate_limiter.py      ← token bucket or semaphore wrapper
    report.json            ← generated output (gitignore this)

  This structure is a suggestion. You can reorganize it — but have a reason for your choices.

---

## After you finish

  Look at your code and ask:
    - Could you swap out JSONPlaceholder for a real API with minimal changes?
    - Could you add a new data source by only touching the fetchers/ folder?
    - Is your circuit breaker reusable for any async function, not just HTTP?
    - Could you run this as a FastAPI background task with zero changes to the core logic?

  If you can answer yes to all of these — you're ready to integrate this into FastAPI.
