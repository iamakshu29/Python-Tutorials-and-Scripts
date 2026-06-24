# 01_learning_asyncio_advanced.py — Advanced asyncio Patterns

import asyncio
import time
import random

# =============================================
# 1. asyncio.Task — Deeper Understanding
# =============================================
# create_task() wraps a coroutine in a Task and schedules it on the event loop immediately.
# A task runs concurrently alongside the coroutine that created it.
#
# Key methods:
# task.cancel()      → Requests cancellation by injecting CancelledError at the next await
# task.cancelled()   → True if the task ended due to cancellation
# task.done()        → True if the task has reached any terminal state (finished, cancelled, or errored)
# task.result()      → Returns the coroutine's return value (does NOT wait — task must already be done)
# task.exception()   → Returns the exception raised by the coroutine, or None
#
# NOTE: Awaiting a cancelled task re-raises CancelledError to the caller.
# NOTE: task.result() vs await task — await waits; result() only retrieves from an already-done task.


async def topic_1():
    print("Topic 1")
    await asyncio.sleep(1)


async def topic_2():
    print("Topic 2")
    await asyncio.sleep(1)
    return "done"


async def topic_3():
    print("Topic 3")
    await asyncio.sleep(1)


async def main():
    task_1 = asyncio.create_task(topic_1())
    task_2 = asyncio.create_task(topic_2())
    task_3 = asyncio.create_task(topic_3())

    await asyncio.gather(task_2, task_3)  # Let task_2 and task_3 finish; task_1 is still running

    task_1.cancel()   # Injects CancelledError into task_1 at its next await
    try:
        await task_1  # Re-raises CancelledError here
    except asyncio.CancelledError:
        print("Task was cancelled")

    print("is the task_1 cancelled ? ", task_1.cancelled())  # True
    print("is the task_1 done ? ", task_1.done())            # True (cancelled = terminal state)

    print("Are other tasks done ? ", task_2.done() and task_3.done())  # True

    print("Task 2 result ", task_2.result())       # Returns the return value
    print("Task 3 any exception ? ", task_3.exception())  # None — no exception was raised


# asyncio.run(main())


# =============================================
# 2. asyncio.TaskGroup — Structured Task Management
# =============================================
# TaskGroup is an async context manager that manages a group of tasks together.
# Key difference from gather(): if ONE task fails, ALL other tasks are cancelled immediately.
# The block after the async with exits only after all tasks complete (or fail).
# No explicit await needed — TaskGroup handles it, same as gather().


async def topic_4():
    print("Topic 4")
    await asyncio.sleep(1)
    raise ValueError("Boom")


async def main():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(topic_4())   # Will raise ValueError — causes all other tasks to be cancelled
        t2 = tg.create_task(topic_2())
        tg.create_task(topic_3())

    return t2.result()


# print(asyncio.run(main()))


# =============================================
# 3. asyncio.wait_for() — Timeouts
# =============================================
# Wraps a coroutine or task with a deadline.
# If the coroutine doesn't complete within the timeout, it is cancelled and TimeoutError is raised.
# Use case: prevent an API call or DB query from hanging indefinitely.


async def api_call():
    print("Hitting API for results")
    await asyncio.sleep(3)  # Try by decrease the value less than timeout
    print("Received Response")


async def main():
    start = time.perf_counter()
    task = asyncio.create_task(api_call())
    try:
        await asyncio.wait_for(task, 2)  # Cancels api_call if it takes more than 2 seconds
    except TimeoutError:
        print("Timeout, api_call is taking longer than expected")
    end = time.perf_counter()

    print("Total time taken: ", end - start)

    print(task.done())       # True — task was cancelled, which is a terminal state
    print(task.cancelled())  # True — wait_for cancelled the task when timeout hit


# asyncio.run(main())


# =============================================
# 4. asyncio.shield() — Protecting Against Cancellation
# =============================================
# shield() wraps a coroutine/task to stop outer cancellation from propagating INTO it.
# If the awaiting coroutine is cancelled, the shielded task keeps running.
#
# IMPORTANT: shield() only blocks cancellation from the AWAITER/PARENT.
# If you call task.cancel() directly on the task itself, shield() cannot stop it.
#
# Use case: you're cancelling a parent task but want a cleanup coroutine inside to still finish.


async def worker():
    try:
        print("worker started")
        await asyncio.sleep(2)
        print("worker completed")
        return "done"
    except asyncio.CancelledError:
        print("worker got CancelledError")
        raise


async def main():
    task = asyncio.create_task(worker())

    asyncio.current_task().cancel()  # Requests cancellation of the currently running coroutine (main)

    try:
        await asyncio.sleep(0.5)  # CancelledError is injected here into main
    except asyncio.CancelledError:
        print("Main was cancelled")

    try:
        # await asyncio.shield(task)  # Protects worker from being cancelled when main is cancelled
        await task  # Without shield: worker is also cancelled
    except asyncio.CancelledError:
        print("Main was cancelled")

    print("task.cancelled()", task.cancelled())


# asyncio.run(main())

# =============================================
# SHIELD FLOW — Case Breakdown
# =============================================
# Case 1 (no shield, no extra sleep):
#   main() cancels so fast that worker never gets a chance to start
#   Output: Main was cancelled / task.cancelled() True
#
# Case 1.1 (no shield, with asyncio.sleep(0.5)):
#   Sleep gives the event loop time to start worker before cancellation hits
#   Output: worker started / Main was cancelled / worker completed / task.cancelled() False
#   (task completed before the second await injected CancelledError)
#
# Case 2 (with shield):
#   shield() absorbs the cancellation — worker keeps running after main is cancelled
#   Output: worker started / Main was cancelled / (worker still running)
#   asyncio.run() shutdown then cancels all remaining tasks — worker gets CancelledError


# =============================================
# 5. asyncio.Queue — Producer-Consumer Pattern
# =============================================
# asyncio.Queue is a thread-safe async queue for producer-consumer pipelines.
# Producers put items; consumers get and process them independently.
#
# Methods:
# queue.put(item)     → async, blocks if queue is full
# queue.get()         → async, blocks until an item is available
# queue.put_nowait()  → sync, raises QueueFull immediately if full
# queue.get_nowait()  → sync, raises QueueEmpty immediately if empty
# queue.task_done()   → decrements the unfinished-work counter (pair with every get())
# queue.join()        → blocks until the unfinished-work counter reaches 0
#
# Sentinel pattern: producer puts one None per consumer to signal "no more work — exit".
#
# Counter lifecycle:
# queue.put()       → counter +1
# queue.get()       → no change (item taken but not yet processed)
# queue.task_done() → counter -1  (signals item fully processed)
# queue.join()      → waits until counter == 0


async def producer(queue, num_consumers):
    for i in range(5):
        print(f"Producing {i}")
        await queue.put(i)        # Adds item; counter +1
        await asyncio.sleep(1)
    # One None sentinel per consumer — signals each consumer to exit cleanly
    for _ in range(num_consumers):
        await queue.put(None)


async def consumer(name, queue):
    while True:
        item = await queue.get()           # Blocks until an item is available
        await asyncio.sleep(random.uniform(0.5, 2))

        if item is None:
            queue.task_done()  # None was put() so counter went up — must bring it back down
            break              # task_done() must be BEFORE break; after break is unreachable

        print(f"{name} Consumed {item}")
        queue.task_done()      # Signals that this item has been fully processed; counter -1


async def main():
    queue = asyncio.Queue()
    num_consumers = 3

    producer_task = asyncio.create_task(producer(queue, num_consumers))
    consumer_tasks = []
    for i in range(num_consumers):
        consumer_tasks.append(asyncio.create_task(consumer(str(i), queue)))

    await producer_task      # Wait for producer to finish putting all items

    await queue.join()       # Wait until every item has been processed (counter == 0)

    for task in consumer_tasks:
        await task           # Each consumer has exited via the None sentinel


asyncio.run(main())


# =============================================
# 6. asyncio.Lock — Mutual Exclusion
# =============================================
# Only one coroutine can hold the lock at a time.
# Use async with lock: — acquires on entry, releases on exit (even if an exception occurs).
# Use case: multiple coroutines updating the same shared mutable state.
# Note: count is an int (immutable), so we wrap it in a dict for shared mutable state.


async def task_1(shared, lock):
    print("task_1: wants to update count")
    async with lock:
        current = shared["count"]
        await asyncio.sleep(random.uniform(0.5, 1))  # simulate work while holding lock
        shared["count"] = current + 1
        print(f"task_1: count updated to {shared['count']}")


async def task_2(shared, lock):
    print("task_2: wants to update count")
    async with lock:
        current = shared["count"]
        await asyncio.sleep(random.uniform(0.5, 1))  # simulate work while holding lock
        shared["count"] = current + 1
        print(f"task_2: count updated to {shared['count']}")


async def main():
    lock = asyncio.Lock()
    shared = {"count": 0}

    await asyncio.gather(task_1(shared, lock), task_2(shared, lock))

    print("Final count:", shared["count"])  # Always 2 — lock prevents race conditions


# asyncio.run(main())

# =============================================
# LOCK FLOW — Step-by-Step
# =============================================
# gather(task_1, task_2) starts both concurrently
#
# task_1: print → async with lock (free → acquired) → reads 0 → await sleep → yields
# task_2: print → async with lock (TAKEN → suspends here, waiting for lock)
#
# task_1 resumes: writes count=1 → exits async with → lock released
# task_2 wakes up: acquires lock → reads 1 → await sleep → writes count=2 → lock released
#
# gather finishes: print("Final count: 2")


# =============================================
# 7. asyncio.Semaphore — Rate Limiting
# =============================================
# A Semaphore allows up to N coroutines to enter the block concurrently.
# The rest wait until a slot frees up.
# Primary use case: limit parallel outbound connections or API calls.
# asyncio.Semaphore(3) → max 3 coroutines processing at once.


async def fetch(url, sem):
    print("Trying to fetch url")
    async with sem:  # each coroutine tries to acquire — first 3 get in, rest wait
        print("Fetching URL", url)
        await asyncio.sleep(random.uniform(1, 3))


async def main():
    sem = asyncio.Semaphore(3)  # Max 3 coroutines can be inside the block at once
    urls = ["abc.com", "def.com", "ghi.com", "jkl.com", "mno.com", "pqr.com", "stu.com"]
    tasks = [asyncio.create_task(fetch(url, sem)) for url in urls]  # All 7 tasks created
    await asyncio.gather(*tasks)  # Semaphore ensures only 3 run concurrently at any moment
    print("All url fetched \n")


# asyncio.run(main())


# =============================================
# 8. asyncio.Event — Signaling Between Coroutines
# =============================================
# An Event is a flag that coroutines can wait on.
# Use case: "don't start processing until something else signals you're ready".
#
# event.set()    → signals all waiting coroutines to wake up
# event.wait()   → suspends until set() is called (non-blocking — yields to event loop)
# event.clear()  → resets the flag back to unset
# event.is_set() → returns True/False without waiting
async def get_db(event):
    print("Connecting to DB")
    await asyncio.sleep(2)  # async sleep — doesn't block event loop
    event.set()
    print("DB connected")


async def fetch_data(event):
    print("User Hitting URL")
    await event.wait()  # suspends until get_db calls event.set()
    print("DB is ready, fetching data now")


async def main():
    event = asyncio.Event()
    await asyncio.gather(get_db(event), fetch_data(event))  # run concurrently


# asyncio.run(main())
