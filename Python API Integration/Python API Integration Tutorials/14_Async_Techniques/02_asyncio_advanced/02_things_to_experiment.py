import asyncio

# ----------------------------------------------------------------------
## Task 1
# Cancel a task that's sleeping — does it print its "done/last" message?
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

# Conclusion
# No it will not print its done/last message which is in this case, "Process Finished, Task completed"
# As the task was cancelled before it could resume after asyncio.sleep(2).


# ----------------------------------------------------------------------
## Task 2
# Put more items than consumers can handle in a Queue — what happens?

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

# CONCLUSION:
# Producer put 7 items, 3 consumers each consumed only 1 item = 3 consumed, 4 abandoned.
# Without while True + None sentinel, consumers exit after 1 item.
# Excess items pile up silently — no error, no warning — just data loss.
# Fix: use while True in consumer + put None sentinel per consumer at end of producer.
    
# asyncio.run(main())

# ----------------------------------------------------------------------
## Task 3
# Use a Lock incorrectly (acquire without release) — your code deadlocks. See it happen.

# Example 1 (Simple)
lock = asyncio.Lock()
async def single_task():
    print("Acquiring the lock the first time...")
    await lock.acquire() # State is now LOCKED
    
    # ... code runs, but you forgot to release it ...
    
    print("Attempting to acquire the lock a second time...")
    await lock.acquire() # HANGS FOREVER HERE. The task freezes.
    
    print("This line will never be reached.")

# asyncio.run(single_task())

# Example 2
async def exp_3(task_id,shared,lock):
    print(f"Exp started by task {task_id}")
    await lock.acquire()
    try:
        shared["count"] = shared["count"] + 1
        await asyncio.sleep(2)
    finally:
        # lock.release()
        print("Exp done")

async def main():
    shared = {"count":0}
    lock = asyncio.Lock()

    await asyncio.gather(exp_3("A",shared,lock),exp_3("B",shared,lock))
    
    print(shared)

# asyncio.run(main())

# ----------------------------------------------------------------------
## Task 4
# Use Semaphore(1) — is it the same as a Lock? When would you prefer one over the other?
# Semaphore(1) behaves the same as Lock — only 1 coroutine at a time.
# Prefer Lock when protecting shared mutable state (only 1 should update at a time).
# Prefer Semaphore(N) when rate limiting — allow N coroutines concurrently (e.g. max 5 API calls).

# WHY prefer Lock over Semaphore(1) for shared state?
# Lock has OWNERSHIP — the coroutine that acquires it is the only one that should release it.
# Semaphore has NO ownership — any coroutine can release it, even one that didn't acquire it.
# This makes Lock safer and more expressive for mutual exclusion.
# Also: async with lock always releases on the same block that acquired — no accidental cross-release.
# Rule: protecting shared state → Lock | limiting concurrency to N → Semaphore(N)

# ----------------------------------------------------------------------
## Task 5
# TaskGroup: make one task raise an exception — watch the others get cancelled

async def topic_1():
    print("Topic 1")
    await asyncio.sleep(1)
    raise ValueError("Boom")

async def topic_2():
    print("Topic 2")
    await asyncio.sleep(3)
    print("Topic 2 after await")

async def main():
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(topic_1())
            tg.create_task(topic_2())
    except* ValueError as eg:
        print(f"Caught the error from topic_1: {eg.exceptions}")

    print("All tasks finished! Final shared state")

asyncio.run(main())

## Conclusion
# If a task finishes successfully before an error happens, it stays successful.
# If a task is still running when a sibling task raises an exception, it is immediately cancelled.