# Module 04 — Concurrency Patterns

## Before you start — you must be comfortable with:

  - asyncio gather, create_task, Semaphore, Queue               (Modules 01 + 02)
  - httpx.AsyncClient for making concurrent HTTP requests        (Module 03)
  - What I/O-bound vs CPU-bound means at a conceptual level
  - Python threading basics (even just the concept — you don't need deep knowledge)

  This module is about knowing WHICH tool to use for WHICH problem.
  asyncio is not always the answer. This module tells you when it isn't.

---

## What this module covers

  Real-world concurrency isn't just "use asyncio".
  Sometimes you need threads. Sometimes you need processes.
  This module teaches you how to choose and how to combine them.

---

## Concepts to Master

  1. I/O-bound vs CPU-bound — the most important distinction
       - I/O-bound: your program spends time WAITING (network, disk, database)
         → asyncio is perfect: while one coroutine waits, others run
       - CPU-bound: your program spends time COMPUTING (image processing, ML, parsing)
         → asyncio is USELESS here: the event loop is blocked by your calculation
         → You need threads or processes for CPU-bound work
       - Test yourself: for each task, say out loud whether it's I/O or CPU bound
         (reading a file, hashing a password, calling an API, sorting a list, resizing an image)

  2. asyncio + ThreadPoolExecutor — run blocking code without blocking the loop
       - import concurrent.futures; executor = concurrent.futures.ThreadPoolExecutor()
       - loop = asyncio.get_event_loop()
       - result = await loop.run_in_executor(executor, blocking_function, arg1, arg2)
       - OR the modern way: await asyncio.to_thread(blocking_function, arg1, arg2)
       - Use case: calling a sync library (e.g., old database driver) from async code
       - Understand: the function runs in a thread, but you await it from your coroutine

  3. asyncio + ProcessPoolExecutor — true parallelism for CPU-bound work
       - Context Manager is use for ProcessPoolExecutor -> with concurrent.futures.ProcessPoolExecutor() as executor:
       - Same interface as ThreadPoolExecutor but uses separate processes
       - Bypasses the GIL — actual parallel CPU execution
       - Use case: image resizing, data transformation, ML inference
       - Cost: process startup overhead, no shared memory — data must be serializable
       - await loop.run_in_executor(process_executor, cpu_intensive_function, data)

  4. asyncio.gather vs asyncio.wait (bit Tricky)
       - asyncio.wait runs a collection of awaitables concurrently and returns two sets: done and pending. Unlike asyncio.gather, it gives you fine-grained control over when to stop waiting.
       - gather: run all, wait for ALL to finish, return results in order
         → if one fails (and return_exceptions=False), it raises immediately
       - asyncio.wait: more control — you define conditions
         → asyncio.FIRST_COMPLETED: returns as soon as ONE finishes
         → asyncio.FIRST_EXCEPTION: returns as soon as one raises
         → asyncio.ALL_COMPLETED: same as gather but gives you futures instead of results
       - Use wait when you want to process results AS THEY COMPLETE
       - syntax
          - done, pending = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)

  5. asyncio.as_completed()
       - Takes a list of coroutines, yields futures as each one finishes
       - for future in asyncio.as_completed(coros): result = await future
       - Perfect for: "show results as they arrive" (like a progress feed)
       - The order of results is NOT the order of input — it's arrival order

  ---
  WHY SO MANY WAYS TO GET RESULTS FROM ASYNC TASKS?

  Because different situations need different levels of control over WHEN you get results:

    create_task + await
       → You start tasks manually and collect results manually one by one.
         All tasks run in parallel (create_task starts them immediately),
         but YOU decide when to await each one.
         Best when you have a small fixed number of tasks and need each result separately.

    gather
       → You hand over a list of tasks and get ALL results back at once — but only
         after the SLOWEST task finishes. Simple, clean, no manual awaiting.
         Best when you need everything before you can proceed (e.g., fetch user + profile + settings).

    TaskGroup (Python 3.11+)
       → Same as gather but safer — if one task crashes, all others are cancelled.
         Best when all tasks must succeed together or not at all.

    wait
       → Like gather but YOU control when to stop waiting.
         Returns (done, pending) sets so you can cancel leftovers or await them later.
         Best when you want "give me the first result and cancel the rest" or need a timeout.

    as_completed
       → You don't wait for all tasks — you process each result the MOMENT it's ready.
         The slowest task doesn't block you from seeing the fast ones.
         Best for: bulk API calls, webhooks, live feeds — anywhere results should
         be handled as they arrive, not all at once at the end or manually.

  One-line rule:
    Need everything at once?        → gather / TaskGroup
    Need first result only?         → wait with FIRST_COMPLETED
    Need each result as it arrives? → as_completed
  ---

  6. Rate limiting patterns
       - Pattern 1: Semaphore — limit concurrent tasks (you know this from Module 02)
       - Pattern 2: Token bucket — more sophisticated; allows bursts up to a limit
         (implement this yourself: refill tokens at a rate, each request costs a token)
       - Pattern 3: asyncio.sleep between requests — simple but effective
       - Real world: most public APIs have rate limits (e.g., 100 requests/minute)
         Know how to read a rate limit header and respect it

  7. Producer-consumer with backpressure
       - Backpressure: the producer slows down when the consumer can't keep up
       - asyncio.Queue has a maxsize parameter — put() will BLOCK if queue is full
       - This is backpressure built in: the producer waits instead of flooding memory
       - Understand: without maxsize, a fast producer can fill memory before consumers catch up
       - Practice: set Queue(maxsize=5) with a fast producer and a slow consumer — watch it

  8. Circuit breaker pattern (conceptual + implementation) (IMPORTANT For Interview Discussion)
       - Problem: if a service is down, you keep hammering it with requests (and failing fast)
       - Circuit breaker: after N failures, "open" the circuit — stop trying for a cooldown period
       - States: CLOSED (normal) → OPEN (failing, don't try) → HALF-OPEN (test one request)
       - Implement a simple CircuitBreaker class that wraps an async function
       - This is a real pattern used in microservices — know it well

---

## Things to experiment with (break stuff on purpose)

  - Run a CPU-heavy loop inside an async function — watch it block other coroutines
  - Move the CPU-heavy loop to ProcessPoolExecutor (via loop.run_in_executor) — watch others run freely (true parallelism, bypasses GIL)
  - as_completed with httpbin delays: send requests with delays [3,1,2,1,3]
    — results should come back in order: 1,1,2,3,3 not 3,1,2,1,3
  - Build a token bucket with a very low refill rate and watch requests get throttled

---

## Key mental models

  The GIL (Global Interpreter Lock):
    Python only runs ONE thread at a time for Python code.
    Threads help with I/O-bound because threads release the GIL while waiting.
    Threads do NOT help with CPU-bound — use processes for that.
    asyncio avoids threads entirely — one thread, cooperative multitasking.

  When to use what:
    I/O-bound, async-friendly libraries → asyncio (your primary tool)
    I/O-bound, sync/blocking libraries → asyncio.to_thread (wrap in thread)
    CPU-bound, smaller data            → ProcessPoolExecutor
    CPU-bound, large data              → separate service / message queue

---

## Vocabulary you must know cold

  GIL                  — Global Interpreter Lock; limits true thread parallelism in Python
  backpressure         — mechanism to slow producers when consumers can't keep up
  circuit breaker      — pattern to stop calling a failing service temporarily
  token bucket         — rate limiting strategy that allows controlled bursts
  as_completed         — process results in arrival order, not submission order
  FIRST_COMPLETED      — asyncio.wait condition: return when first task finishes

---

## Mini Project — Rate-Limited Concurrent API Fetcher

  Build a system that fetches data from many URLs concurrently with rate limiting.

  Requirements:
    - A list of 30 URLs (use httpbin.org/delay/N with N between 0-3 and /get endpoints)
    - Fetch ALL of them concurrently — but no more than 5 at a time (Semaphore)
    - Additionally, enforce a rate limit of no more than 10 requests per 10 seconds
      (implement this as a simple token bucket or a counter + sleep approach)
    - Process and print results AS THEY COMPLETE (use as_completed)
    - Track: total requests, successful, failed, avg response time
    - If a request fails, retry once after 1 second

  Stretch goals:
    - Add a circuit breaker: after 3 consecutive failures to the same host, 
      stop trying for 30 seconds, then try once (half-open)
    - One of your URLs should point to a "slow" httpbin endpoint —
      use asyncio.to_thread to run a CPU-heavy operation (e.g., sha256 hashing)
      on each response body without blocking the event loop
    - Save all results to a JSON file as they arrive (not all at the end)
    - Print a live progress counter: "Completed: 12/30"

  File to create: 04_concurrency_patterns/rate_limited_fetcher.py

---

## You're ready for Module 05 when:

  - You can explain GIL, and why asyncio.to_thread exists
  - You've implemented a circuit breaker (even a basic one)
  - You understand the difference between gather and as_completed
  - You know when asyncio alone is NOT enough and when to reach for threads/processes
  - Your mini project respects rate limits correctly
