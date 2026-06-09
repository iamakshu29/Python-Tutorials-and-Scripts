# Module 05 — Async Context Managers & Async Iterators

## Before you start — you must be comfortable with:

  - Regular context managers (__enter__, __exit__, @contextmanager)  (14_context_managers.py)
  - Generators (yield, next(), StopIteration)                         (09_generators.py)
  - asyncio core (event loop, await, coroutines)                     (Module 01)
  - asyncio.Queue for streaming patterns                             (Module 02)

  This module is the "glue" layer — it teaches you how to build async-aware
  abstractions that other code can use cleanly.
  Everything in httpx, SQLAlchemy async, aiofiles uses these patterns internally.

---

## What this module covers

  How to build and USE async context managers and async iterators.
  After this, you'll understand how async with and async for actually work
  and be able to build your own — which is essential for FastAPI middleware,
  database session management, and streaming APIs.

---

## Concepts to Master

  1. Async context managers — the protocol
       - A class needs: __aenter__(self) and __aexit__(self, exc_type, exc_val, exc_tb)
       - Both must be async (defined with async def)
       - async with MyManager() as resource: ...
       - Use case: any resource that needs async setup and async teardown
         (database connections, HTTP sessions, file locks, WebSocket connections)
       - Compare with sync: __enter__/__exit__ vs __aenter__/__aexit__

  2. @asynccontextmanager decorator
       - From contextlib import asynccontextmanager
       - Write a generator function with async def + yield
       - Code before yield = setup (__aenter__)
       - Code after yield = teardown (__aexit__)
       - MUCH simpler than writing a full class for simple cases
       - You've seen this in FastAPI: @asynccontextmanager for lifespan events

  3. Exception handling in async context managers
       - __aexit__ receives exception info — you can suppress or re-raise
       - Return True from __aexit__ to suppress the exception
       - If you don't return True (or return None/False), the exception propagates
       - Understand: this is identical to sync context managers, just async

  4. Async iterators — the protocol
       - A class needs: __aiter__(self) and __anext__(self)
       - __aiter__ returns self (like __iter__)
       - __anext__ returns the next value OR raises StopAsyncIteration
       - async for item in MyIterator(): ...
       - Use case: paginated API results, WebSocket messages, log streams, file chunks

  5. Async generators
       - async def with yield — the async version of a generator function
       - Much simpler than writing a class with __aiter__ and __anext__
       - async def read_lines(file): yield line (simplified — file reading is async)
       - async for line in read_lines(file): process(line)
       - IMPORTANT: async generators are lazy — they produce values on demand
       - Use case: streaming large datasets without loading all into memory

  6. Combining async generators with Queues
       - An async generator can pull from a Queue — turns a push model into a pull model
       - Producer pushes to queue; your async generator pulls and yields
       - Consumer does async for item in generator() — clean, readable

  7. aiofiles — async file I/O
       - pip install aiofiles
       - async with aiofiles.open("file.txt") as f: content = await f.read()
       - async for line in f: ... — async iteration over file lines
       - Why: regular open() + read() blocks the event loop
       - Understand: disk I/O is blocking by default in Python — aiofiles wraps it in a thread

  8. asyncio.timeout (Python 3.11+) as a context manager
       - async with asyncio.timeout(5.0): await slow_operation()
       - Cleaner than asyncio.wait_for for surrounding a block of code
       - Raises TimeoutError on expiry

---

## Things to experiment with (break stuff on purpose)

  - Write a class with __aenter__ and __aexit__ — use it with async with
  - Write the same thing with @asynccontextmanager — notice how much shorter it is
  - Raise an exception inside async with — does __aexit__ get called? (Yes — verify it)
  - Write an async generator that yields 10 items — consume with async for
  - Break out of an async for loop early — does the generator clean up?
    (Use try/finally in the generator to check)
  - Use aiofiles to read a large text file line by line without loading it all into memory

---

## Key mental models

  async with is for resources that need async setup/teardown.
  async for is for sequences that are produced asynchronously (streams, pages, messages).

  The async generator pattern is the single most powerful tool for streaming:
    - Your FastAPI endpoint can stream a response using an async generator
    - Your HTTPX client can stream downloads using an async generator
    - Your WebSocket handler receives messages using an async generator

  Think of async generators as "async pipelines":
    async_source → async_transform → async_sink
    Each stage yields to the next, nothing is loaded all at once.

---

## Vocabulary you must know cold

  __aenter__ / __aexit__      — the async context manager protocol
  __aiter__ / __anext__       — the async iterator protocol
  StopAsyncIteration          — exception that ends an async for loop
  async generator             — async def + yield; simplest way to make an async iterator
  aiofiles                    — library for non-blocking file I/O in asyncio
  lazy evaluation             — produce values on demand, not all at once

---

## Mini Project — Async Log Stream Processor

  Build a system that asynchronously reads, filters, and processes log lines.

  Requirements:
    - Create a sample log file with 1000+ lines (you can generate it with a sync script)
      Each line format: [TIMESTAMP] [LEVEL] [SERVICE] MESSAGE
      Levels: INFO, WARNING, ERROR, DEBUG
    - Write an async generator that reads the file line by line (use aiofiles)
    - Write another async generator that filters lines by level
      (takes the first generator as input, yields only matching lines)
    - Write an async generator that parses each line into a dict
    - Chain them: read → filter → parse (async pipeline)
    - Process all ERROR lines concurrently: for each error, simulate sending an alert
      (asyncio.sleep to simulate) — limit to 3 concurrent alerts (Semaphore)
    - Track and print stats: total lines, lines per level, errors alerted, processing time

  Stretch goals:
    - Write a custom async context manager class (not decorator) that:
      opens the log file on __aenter__, closes it on __aexit__
      and provides an async generator method to iterate lines
    - Add a "live tail" mode: keep the file open and watch for new lines every second
      (like tail -f) using asyncio.sleep in a loop
    - Support multiple log files concurrently — process all with TaskGroup
    - Write processed results to an output file using aiofiles (while reading input)

  File to create: 05_async_context_managers/log_stream_processor.py

---

## You're ready for the Final Project when:

  - You can write a custom async context manager both as a class AND with the decorator
  - You can build an async pipeline using chained async generators
  - You understand why aiofiles exists (blocking I/O problem)
  - You've chained at least 3 async generators together
  - Your log processor correctly pipelines without loading the whole file into memory
