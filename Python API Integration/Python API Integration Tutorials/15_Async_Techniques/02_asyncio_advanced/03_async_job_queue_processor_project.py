# 03_async_job_queue_processor_project.py — Async Job Queue Processor

# =============================================
# PROJECT OVERVIEW
# =============================================
# Simulates a real-world async job queue: a producer enqueues jobs; multiple consumers
# process them concurrently with rate limiting (Semaphore), retry logic, and a startup
# gate (Event) so consumers don't poll before any jobs are available.
# Uses TaskGroup for structured teardown — all tasks are cancelled if one fails.

import asyncio
import random


# =============================================
# JOB LIST — Input Data
# =============================================
# 20 jobs; most are type "email", one is type "message" (used to demo a slow job).
jobs = [
    {"id": 1, "type": "email", "payload": "..."},{"id": 2, "type": "email", "payload": "..."},
    {"id": 3, "type": "email", "payload": "..."},{"id": 4, "type": "email", "payload": "..."},
    {"id": 5, "type": "email", "payload": "..."},{"id": 6, "type": "email", "payload": "..."},
    {"id": 7, "type": "message", "payload": "..."},{"id": 8, "type": "email", "payload": "..."},
    {"id": 9, "type": "email", "payload": "..."},{"id": 10, "type": "email", "payload": "..."},
    {"id": 11, "type": "email", "payload": "..."},{"id": 12, "type": "email", "payload": "..."},
    {"id": 13, "type": "email", "payload": "..."},{"id": 14, "type": "email", "payload": "..."},
    {"id": 15, "type": "email", "payload": "..."},{"id": 16, "type": "email", "payload": "..."},
    {"id": 17, "type": "email", "payload": "..."},{"id": 18, "type": "email", "payload": "..."},
    {"id": 19, "type": "email", "payload": "..."},{"id": 20, "type": "email", "payload": "..."}
    ]

# =============================================
# PRODUCER — Enqueues Jobs
# =============================================
# Puts each job into the queue with a random delay simulating new job arrivals.
# Once all jobs are queued, sets the Event to unblock consumers.
# Then puts one None sentinel per consumer to signal clean shutdown.
async def producer(queue, num_consumers, event):
    print("Start producing Jobs")
    for job in jobs:
        await queue.put(job)
        await asyncio.sleep(random.uniform(0.5, 2))
    event.set()                      # Stretch Goal 3: signal all jobs are queued, consumers can start
    for _ in range(num_consumers):   # One None sentinel per consumer — triggers their exit loop
        await queue.put(None)
    print("Producer done")

# =============================================
# CONSUMER — Processes Jobs with Rate Limiting and Retry
# =============================================
# Each consumer waits for the Event before starting, then loops:
#   1. Gets a job from the queue
#   2. Exits on None sentinel
#   3. Acquires the Semaphore (max 3 concurrent processors)
#   4. Processes the job; on failure re-queues up to 2 retries before dropping
#   5. Calls task_done() to decrement the queue's unfinished-work counter
#
# NOTE: Semaphore is inside the loop, not around get() — consumers can freely
# grab jobs from the queue; only the actual processing is rate-limited to 3 at once.
async def consumer(user_id, queue, sem, event):
    print(f"Consumer {user_id} started")
    while True:
        await event.wait()    # Stretch Goal 3: block until producer signals all jobs are queued
        result = await queue.get()

        if result is None:           # Sentinel — exit cleanly
            queue.task_done()        # None was put(), counter went up — must bring it down
            break                    # task_done() MUST be before break; after break is unreachable

        async with sem:              # Rate limit: only 3 consumers process simultaneously
            if result["type"] == "message":  # Stretch Goal 1: slow job type
                print(f"Consumer {user_id} processing job {result['type']}")
                await asyncio.sleep(3)
                print(f"Consumer {user_id} done with job {result['type']}")
            else:
                print(f"Consumer {user_id} processing job {result['id']}")
                await asyncio.sleep(random.uniform(0.5, 2))
        # Stretch Goal 2: 30% random failure — re-queue up to 2 retries, then drop
                if random.random() < 0.3:
                    retries = result.get("retries", 0)
                    if retries < 2:
                        result["retries"] = retries + 1
                        print(f"Job {result['id']} failed → retry {result['retries']}/2, re-queuing")
                        await queue.put(result)  # Re-queue for retry (counter goes up again)
                    else:
                        print(f"Job {result['id']} failed after 2 retries → dropping")
                else:
                    print(f"Consumer {user_id} done with job {result['id']}")

        queue.task_done()  # Every get() needs a matching task_done() — decrements counter

# =============================================
# ENTRY POINT
# =============================================
# TaskGroup runs producer + all consumers concurrently.
# TaskGroup exits only when all tasks complete (or cancels all if one fails).
# Stretch Goal 4: already covered by the TaskGroup + None sentinel pattern.
async def main():
    num_consumers = 4
    sem = asyncio.Semaphore(3)  # Max 3 consumers processing at once
    queue = asyncio.Queue()
    event = asyncio.Event()     # Gate: consumers wait until producer signals jobs are ready

    async with asyncio.TaskGroup() as tg:
        tg.create_task(producer(queue, num_consumers, event))
        for i in range(1, num_consumers + 1):
            tg.create_task(consumer(i, queue, sem, event))

    print("All jobs consumed")

asyncio.run(main())
    
# Stretch Goal 4 → Already implemented with TaskGroup and None sentinel pattern