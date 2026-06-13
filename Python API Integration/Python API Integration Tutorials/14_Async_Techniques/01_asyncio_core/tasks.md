# Module 01 — asyncio Core

## Before you start — you must be comfortable with:

  - What a generator is and how yield pauses a function         (09_generators.py)
  - What a context manager is and how __enter__/__exit__ works  (14_context_managers.py)
  - How decorators wrap functions                               (11_decorators.py)
  - Python's regular function call stack (call → return → next call)

  If any of the above feel fuzzy, revisit those files first.
  asyncio is built on generators under the hood — understanding yield makes async/await click.

---

## What this module covers

  The event loop, coroutines, awaiting things, running tasks concurrently with gather.
  This is the absolute foundation. Everything else in this path depends on it.

---

## Concepts to Master

  Work through these in order. For each one, write a small script and run it.

  1. async def and coroutine objects
       - Define a function with async def
       - Notice what calling it returns (it doesn't run yet — it returns a coroutine object)
       - Understand WHY it doesn't run immediately

  2. asyncio.run()
       - This creates the event loop and runs a coroutine from sync code
       - You will almost always use this as your entry point
       - Understand: there can only be ONE event loop per thread

  3. await keyword
       - You can only use await inside an async def function
       - await pauses YOUR coroutine and gives control back to the event loop
       - The event loop can run something else while you're waiting
       - Understand the difference: time.sleep() BLOCKS, asyncio.sleep() YIELDS

  4. Coroutine chaining
       - One async function calling another with await
       - Build a chain: main → fetch_data → parse_response
       - Trace what happens at each await

  5. asyncio.gather()
       - Run multiple coroutines CONCURRENTLY (not in parallel — important distinction)
       - Understand: concurrent means interleaved, not simultaneous
       - Try: run 3 coroutines that each sleep for 2 seconds
         - With gather: total time ~2s
         - Without gather (sequential awaits): total time ~6s
       - Know what gather returns (a list of results)

  6. asyncio.create_task()
       - Schedule a coroutine to run "in the background"
       - Understand the difference from just calling await coroutine()
       - Task starts immediately when the event loop gets a chance
       - You can await the task later to get its result

  7. Timing and understanding the event loop
       - Use time.perf_counter() to measure actual elapsed time
       - See concurrency vs sequential with your own timings
       - Print statements to trace which coroutine is running when

---

## Things to experiment with (break stuff on purpose)

  - Call an async function without await — what happens?
  - Use time.sleep() inside an async function — what does it do to other coroutines?
  - What happens if you raise an exception inside a gather?
  - What is the return value of a coroutine that has no return statement?

---

## Key mental model

  Think of the event loop as a to-do list manager.
  Every time a coroutine hits await, it says "I'm waiting, do something else".
  The event loop picks the next ready coroutine and runs it until it hits an await.
  No two coroutines run at the EXACT same instant — they take turns.
  This is why asyncio is great for I/O (waiting for network, disk) but NOT for CPU work.

---

## Vocabulary you must know cold

  coroutine      — an async def function (or the object it returns when called)
  event loop     — the scheduler that runs coroutines
  await          — suspend this coroutine, let others run
  task           — a coroutine wrapped and scheduled by the event loop
  concurrent     — multiple things making progress by interleaving (not truly simultaneous)
  parallel       — multiple things running at the exact same time (different CPU cores)

---

## Mini Project — Async Task Runner

  Build a small script that simulates running "jobs" concurrently.

  Requirements:
    - Define at least 4 async "job" functions (e.g., fetch_users, process_orders, send_emails, generate_report)
    - Each job should take a different amount of simulated time (use asyncio.sleep)
    - Each job should print when it starts and when it finishes
    - Run all jobs concurrently using gather
    - Print the total elapsed time at the end
    - Compare: also run them sequentially and print that total time

  Stretch goals (do these once the basic version works):
    - Some jobs depend on others (e.g., generate_report needs fetch_users to finish first)
      → figure out how to structure that with gather and await
    - One job should "fail" — handle the error without stopping all other jobs
    - Add a job that updates a shared counter (and notice if there are race conditions)
    Define - A race condition is when two or more concurrent operations read and modify the same value, and the final result depends on who runs in what order — giving you a wrong answer.

  File to create: 01_asyncio_core/async_task_runner.py

---

## You're ready for Module 02 when:

  - You can explain what the event loop does without looking anything up
  - You know the difference between await coroutine() and task = create_task(coroutine())
  - You understand WHY gather is faster than sequential awaits
  - Your mini project works and you can explain every line
