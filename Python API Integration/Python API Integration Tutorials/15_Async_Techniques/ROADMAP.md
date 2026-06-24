# Async Techniques — Learning Roadmap

You already know:
  - requests, auth, exceptions, logging, env, classes
  - retry logic, pathlib, generators, first-class functions
  - decorators, static typing, context managers

This path builds directly on top of those. Work through each module IN ORDER.
Each module has a tasks.md file. Write all code yourself.

---

## Module Order

  01_asyncio_core/          → the foundation — do NOT skip or rush this
  02_asyncio_advanced/      → control flow, queues, synchronization
  03_httpx/                 → async HTTP — replaces requests for async code
  04_concurrency_patterns/  → real-world strategies for parallel work
  05_async_context_managers → async with, async for, async generators

---

## Mini Projects (one per module)

  Each module ends with a mini project. Build it BEFORE moving to the next module.
  The mini projects are intentionally small — the goal is applying one skill at a time.

  01 → Async Task Runner (asyncio core)
  02 → Async Job Queue Processor (asyncio advanced)
  03 → Multi-Endpoint Health Checker (httpx)
  04 → Rate-Limited Concurrent Fetcher (concurrency patterns)
  05 → Async Log Stream Processor (async iterators)

---

## Final Project

  FINAL_PROJECT/
    Async API Aggregator — combines all 5 modules into one real-world service.
    Do this ONLY after finishing all 5 mini projects.

---

## Rules for yourself

  - Write every single line yourself. No copy-paste.
  - If something doesn't work, read the error, don't google immediately.
  - Comment WHY you wrote something, not what it does.
  - Each mini project should feel slightly uncomfortable — that's the point.

---

## NOTE — What comes AFTER this path (when integrating into FastAPI)

  This path intentionally skips one thing: async database access.
  Once you finish here and move to FastAPI projects, you'll need:

  SQLAlchemy async + asyncpg (PostgreSQL)
    - pip install sqlalchemy[asyncio] asyncpg
    - AsyncEngine, AsyncSession — the async versions of what you already know from your todo app
    - async with AsyncSession() as session: → this is just an async context manager (Module 05)
    - await session.execute(), await session.commit(), await session.close()
    - The async concepts are NOT new at that point — only the SQLAlchemy API is new

  Where to learn it:
    - SQLAlchemy docs: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
    - Look at your existing FastAPI projects (02_Job_Application_Tracker etc.)
      and think about how you'd rewrite the DB layer using AsyncSession instead of Session

  The hard part (understanding what async with session: actually does) will be solved
  by the time you finish this path. Adding SQLAlchemy async on top is just API learning.
