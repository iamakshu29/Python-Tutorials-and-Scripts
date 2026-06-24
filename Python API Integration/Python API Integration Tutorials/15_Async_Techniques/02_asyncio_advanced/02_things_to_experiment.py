# 02_things_to_experiment.py — Experiments: Break Things on Purpose

import asyncio

# =============================================
# EXP 1: Cancel a Sleeping Task
# =============================================
# Does a cancelled task still print its final "done" message?
async def exp_1():
    print("Task Started, ready to process")
    await asyncio.sleep(2)
    print("Process Finished, Task completed")

async def main():
    task = asyncio.create_task(exp_1())
    task.cancel()
    # try:
    #     await task
    # except asyncio.CancelledError:
    #     print("Task was cancelled")
    print("is cancelled ??", task.cancelled())
    print("is done ??", task.done())

# asyncio.run(main())

# Conclusion: No, the final message is never printed.
# The task was cancelled before it could resume after asyncio.sleep(2).


# =============================================
# EXP 2: More Items Than Consumers Can Handle
# =============================================
# Producer puts 7 items; only 3 consumers, each consuming just 1.
# What happens to the remaining items?
async def producer(queue):
    print("Sending results")
    for i in range(1,8):
        await queue.put(i)
        await asyncio.sleep(1)

async def consumer(num, queue):
    print(f"Consumer {num} start receiving")
    await queue.get()
    

async def main():
    queue = asyncio.Queue()
    producer_task = asyncio.create_task(producer(queue))

    consumer_tasks = []
    for i in range(1,4):
        consumer_tasks.append(asyncio.create_task(consumer(i,queue)))

    await producer_task
    print("Producer finished producing result")

    for task in consumer_tasks:
        await task
    print("Received all results")

    print("Items left in queue (unprocessed):", queue.qsize())  # 4 items abandoned

# Conclusion:
# Producer put 7 items; 3 consumers each consumed 1 = 3 consumed, 4 silently abandoned.
# No error, no warning — excess items just pile up in the queue.
# Fix: use while True in consumer + one None sentinel per consumer at the end of producer.
    
# asyncio.run(main())

# =============================================
# EXP 3: Lock Deadlock — Acquire Without Release
# =============================================
# What happens if a coroutine tries to acquire a lock it already holds?
# Or if it forgets to release? — The event loop stalls forever.

# Example 1: Same coroutine acquiring the same lock twice
lock = asyncio.Lock()
async def single_task():
    print("Acquiring the lock the first time...")
    await lock.acquire()  # Lock is now LOCKED
    
    # ... lock is never released ...
    
    print("Attempting to acquire the lock a second time...")
    await lock.acquire()  # DEADLOCK — hangs forever waiting for itself
    
    print("This line will never be reached.")

# asyncio.run(single_task())

# Example 2: Two coroutines sharing a lock — one forgets to release
async def exp_3(task_id,shared,lock):
    print(f"Exp started by task {task_id}")
    await lock.acquire()
    try:
        shared["count"] = shared["count"] + 1
        await asyncio.sleep(2)
    finally:
        # lock.release()  # Commented out — task B waits forever for this lock
        print("Exp done")

async def main():
    shared = {"count":0}
    lock = asyncio.Lock()

    await asyncio.gather(exp_3("A",shared,lock),exp_3("B",shared,lock))
    
    print(shared)

# asyncio.run(main())

# =============================================
# EXP 4: Semaphore(1) vs Lock
# =============================================
# Semaphore(1) and Lock both allow only 1 coroutine at a time — but they differ in ownership.
# Lock has OWNERSHIP: the coroutine that acquires it must be the one to release it.
#   → Safer for protecting shared mutable state — prevents accidental cross-release.
# Semaphore has NO OWNERSHIP: any coroutine can release it, even one that didn't acquire it.
#   → Use when rate-limiting concurrency to N (e.g. max 5 API calls at once).
#
# Rule of thumb:
# Protecting shared state  → use Lock
# Limiting concurrency to N  → use Semaphore(N)

# =============================================
# EXP 5: TaskGroup — One Failure Cancels All
# =============================================
# If one task raises an exception inside a TaskGroup, all sibling tasks are immediately cancelled.
# Tasks that already completed successfully before the error stay in their completed state.
async def topic_1():
    print("Topic 1")
    await asyncio.sleep(1)
    raise ValueError("Boom")

async def topic_2():
    print("Topic 2")
    await asyncio.sleep(3)
    print("Topic 2 after await")  # Never reached — cancelled when topic_1 raises

async def main():
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(topic_1())
            tg.create_task(topic_2())
    except* ValueError as eg:
        print(f"Caught the error from topic_1: {eg.exceptions}")

    print("All tasks finished! Final shared state")

asyncio.run(main())

# Conclusion:
# topic_1 raises after 1s — topic_2 is still sleeping at 3s, so it gets cancelled.
# If topic_2 had already finished before topic_1 raised, it would remain successful.