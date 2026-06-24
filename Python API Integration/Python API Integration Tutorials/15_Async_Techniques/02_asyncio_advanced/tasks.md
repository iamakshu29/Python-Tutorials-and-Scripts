# Module 02 — asyncio Advanced

## Before you start — you must be comfortable with:

  - Everything from Module 01 (event loop, coroutines, gather, tasks)
  - You should have finished the async_task_runner mini project
  - Python's built-in Queue concept (even the sync version from queue.Queue is fine)
  - What a Lock is conceptually (mutual exclusion — only one thing at a time)

  If gather still feels like magic, go back. This module uses it heavily.

---

## What this module covers

  Real-world async patterns: controlling tasks, synchronizing coroutines,
  building producer-consumer pipelines, handling timeouts gracefully.
  These are the tools you'll reach for in every real async application.

---

## Concepts to Master

  1. asyncio.Task — deeper understanding
       - create_task() schedules a coroutine; it runs concurrently with you
       - task.cancel() — how to cancel a running task
       - task.cancelled(), task.done(), task.result(), task.exception()
       - CancelledError — what it is and how to handle it in the cancelled task
       - Understand: cancelling a task doesn't kill it instantly — it injects CancelledError at the next await

  2. asyncio.TaskGroup (Python 3.11+)
       - A cleaner way to manage a group of tasks
       - async with asyncio.TaskGroup() as tg: tg.create_task(coro())
       - Key difference from gather: if ONE task fails, ALL others are cancelled
       - Know when to use TaskGroup vs gather (structured vs fire-and-forget)

  3. asyncio.wait_for()
       - Run a coroutine with a timeout
       - It returns a coroutine
       - Raises asyncio.TimeoutError if it takes too long
       - Understand: the coroutine is cancelled when the timeout hits
       - Practice: simulate a slow API call, wrap it in wait_for with 2s timeout

  4. asyncio.shield()
       - Protect a child coroutine from being cancelled
       - Use case: you're cancelling a task but you want the cleanup coroutine inside to finish
       - Understand when shield is NOT enough (it doesn't prevent all cancellations)

  5. asyncio.Queue
       - A queue designed for async producer-consumer patterns
       - Methods: put(), get(), put_nowait(), get_nowait(), task_done(), join()
       - Build a producer that puts items → consumer that gets and processes them
       - Multiple consumers: how does the queue distribute work?
       - Queue.join() — wait until all items have been processed

  6. asyncio.Lock
       - Only one coroutine can hold the lock at a time
       - Use: async with lock:  (yes, it works with async with)
       - When do you need a Lock in async code? (shared mutable state)
       - Contrast with threading.Lock — this one is async-aware

  7. asyncio.Semaphore
       - Like a Lock but allows N coroutines at a time instead of 1
       - Use case: limit concurrent connections to 5 max
       - async with asyncio.Semaphore(5):
       - This is your primary tool for rate limiting — you'll use it constantly

  8. asyncio.Event
      The event is specifically for "don't proceed until something else signals you're ready".
       - A flag that coroutines can wait for
       - event.set() → signals the event — wakes all waiters
       - event.wait() → pauses until the event is set
       - event.clear() → resets the event back to unset
       - event.is_set() → returns True/False
       - Use case: "don't start processing until the database is ready"

---

## Things to experiment with (break stuff on purpose)

  - Cancel a task that's sleeping — does it print its "done/last" message?
  - Put more items than consumers can handle in a Queue — what happens?
  - Use a Lock incorrectly (acquire without release) — your code deadlocks. See it happen.
  - Use Semaphore(1) — is it the same as a Lock? When would you prefer one over the other?
  - TaskGroup: make one task raise an exception — watch the others get cancelled

---

## Key mental model

  asyncio.Queue is your go-to for decoupling work.
  Producers don't care how many consumers there are.
  Consumers don't care how fast producers produce.
  The queue is the buffer between them.

  Semaphore is your go-to for rate limiting.
  "Maximum 5 things happening at once" = Semaphore(5).
  You will use this with httpx in Module 03.

---

## Vocabulary you must know cold

  task cancellation   — injecting CancelledError at the next await point
  TaskGroup           — structured concurrency: tasks live and die together
  timeout             — maximum time allowed before giving up
  producer-consumer   — one side creates work, another side does the work
  semaphore           — a counter that limits concurrent access
  deadlock            — two things waiting on each other forever (know how to avoid it)

---

## Mini Project — Async Job Queue Processor

  Build a job queue where multiple workers consume jobs concurrently.

  Requirements:
    - A producer that puts 20 "jobs" into an asyncio.Queue
      (a job can just be a dict: {"id": 1, "type": "email", "payload": "..."})
    - 4 worker coroutines that consume from the queue concurrently
    - Each worker prints which job it picked up and simulates processing time (asyncio.sleep)
    - Use Queue.join() so main knows when ALL jobs are done
    - Limit max 3 workers processing at the same time using a Semaphore
      (even though you have 4 workers, only 3 can be actively processing)
    - Print which worker processed which job — you should see the distribution

  Stretch goals:
    - One job type ("message") takes longer — workers should not block each other
    - If a job fails (random chance), put it back in the queue for retry (max 2 retries)
    - Add an asyncio.Event that workers wait on before starting
      (simulate a "system ready" signal before processing begins)
    - Graceful shutdown: when the producer is done and queue is empty,
      workers should exit cleanly (not hang forever waiting for more items)

  File to create: 02_asyncio_advanced/job_queue_processor.py

---

## You're ready for Module 03 when:

  - You can build a producer-consumer system with asyncio.Queue without looking up the API
  - You understand when to use Lock vs Semaphore
  - You've actually seen a task get cancelled and handled CancelledError
  - Your mini project distributes work across workers correctly
