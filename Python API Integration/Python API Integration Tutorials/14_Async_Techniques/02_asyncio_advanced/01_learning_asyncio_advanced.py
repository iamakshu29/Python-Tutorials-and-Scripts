import asyncio
import time
import random

### Cancel a running task
# If as task got cancelled, it will not get executed
# The coroutine must hit an await to be injected with CancelledError
# and if we await that task, it raises CancelledError to the caller.

### Why await a cancelled task?
# Without awaiting it, the task may still be running briefly while it handles the cancellation.
# So we ensure the task has completely finished its cleanup and termination.

### A task becomes cancelled only when:
# task.cancel() requests cancellation.
# The coroutine reaches an await/suspension point where CancelledError is injected.
# The CancelledError propagates out of the coroutine (i.e., it is not suppressed).
# The task finishes in the cancelled state.


# task.cancel() -> "request cancellation" by injecting a CancelledError into the task at its next suspension point. i.e. at await
# task.cancelled() -> To check if the tasks is cancelled or not -> bool => True if task ended due to cancellation
# task.done() -> In asyncio, a task is considered done if it has reached any terminal state -> i.e. finished properly or cancelled or it can be in final state, without ever executing a single line of the coroutine.

### To inspect the outcome of a "completed" asyncio.Task
# task.result() ->
# Returns the value returned by the coroutine.
# raises asyncio.CancelledError for a cancelled task

# The key difference between await task and task.result() is:
# await task waits until the task is finished.
# task.result() does not wait. It only retrieves the result of a task that has already "completed".

# task.exception() ->
# If the task raised an exception -> bool


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

    await asyncio.gather(task_2, task_3)

    task_1.cancel()
    try:
        await task_1
    except asyncio.CancelledError:
        print("Task was cancelled")

    print("is the task_1 cancelled ? ", task_1.cancelled())
    print("is the task_1 done ? ", task_1.done())

    print("Are other tasks done ? ", task_2.done() and task_3.done())

    print("Task 2 result ", task_2.result())
    print("Task 3 any exception ? ", task_3.exception())


# asyncio.run(main())

## TaskGroup
# It is an async Context Manager

## Main diff from asyncio.gather() is
# if ONE task fails, ALL others are cancelled
# Means execution after await wont be run

# For gather and TaskGroup we dont need any explicit await to waits until the task is finished.
# For create_task() we need an explicit await, to get the return values or anything


async def topic_4():
    print("Topic 4")
    await asyncio.sleep(1)
    raise ValueError("Boom")


async def main():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(topic_4())
        t2 = tg.create_task(topic_2())
        tg.create_task(topic_3())

    return t2.result()


# print(asyncio.run(main()))


## asyncio.wait_for()
# It does two things:
#     Waits up to N seconds.
#     If the timeout is reached, it will Cancels the task and raise TimeoutError.


async def api_call():
    print("Hitting API for results")
    await asyncio.sleep(3)  # Try by decrease the value less than timeout
    print("Received Response")


async def main():
    start = time.perf_counter()
    task = asyncio.create_task(api_call())
    try:
        await asyncio.wait_for(task, 2)
    except TimeoutError:
        print("Timeout, api_call is taking longer than expected")
    end = time.perf_counter()

    print("Total time taken: ", end - start)

    print(task.done())
    print(task.cancelled())


# asyncio.run(main())


## asyncio.shield()
# Shield() protects us against cancellation propagation from the awaiting or child coroutine.
# If the coroutine doing the await is cancelled, the cancellation stops at the shield boundary. The awaited task keeps running.

# IMP -> shield() does NOT protect against the cancellation requested directly to the task itself. The task will still receive CancelledError and can end in the cancelled state.

## Cancellation of the parent/awaiter
# Without shield(): cancellation propagates into the awaited task.
# With shield(): cancellation does not propagate into the awaited task.

## Cancellation of the task itself
# task.cancel() always targets the task directly.
# shield() cannot intercept or block that.


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

    asyncio.current_task().cancel()

    try:
        await asyncio.sleep(0.5)
    except asyncio.CancelledError:
        print("Main was cancelled")

    try:
        # await asyncio.shield(task)  # protect worker from getting cancelled
        await task  # cancelled worker also
    except asyncio.CancelledError:
        print("Main was cancelled")

    print("task.cancelled()", task.cancelled())


# asyncio.run(main())

# Flow
# asyncio.current_task().cancel() -> requests cancellation of current task i.e. main()
# await task or await asyncio.shield(task) -> CancelledError is injected so main got cancelled()
# print("Main was cancelled") -> ran
# at same time because of await control goes to -> worker

## Case-1 no shield
# but it got cancelled very fast that worker didn't get time to execute and it just print
# Main was cancelled
# task.cancelled() True

## Case- 1.1 To give some time I added another await witha syncio.sleep(0.5)
# Now it has time to run the worker, so output is
# worker started
# Main was cancelled
# worker completed
# task.cancelled() False -> WHY because task is completed before 2nd await and await injected the CancelledError

## Case-2 shield
# comment the first try-catch{} and uncomment shield code
# Flow
# await asyncio.shield(task) injects error and also control goes to worker
# prints
# worker started
# Main was cancelled
# worker's await -> control back to main() -> it will run till it ends or find another await
# task.cancelled() False got print -> func end
## Now shutdown is ran by asyncio.run(main()) -> it will end all running tasks if any (worker is running)
# so it end which cause error -> prints worker got CancelledError


## asyncio.Queue
# left - put_nowait(), get_nowait(),

### Important Explaination
# queue.put()     → counter +1  (item added) -> adding a ticket
# queue.get()     → nothing changes (item taken but not processed yet) -> picking up the ticket
# task_done()     → counter -1  (item fully processed) -> stamping the ticket as "done"
# queue.join()    → waits here until counter == 0 -> waiting until all tickets are stamped

# task_done() — decrements the internal counter (doesn't check anything, just signals "one more item finished")
# queue.join() — blocks until the counter reaches 0 (it's a waiter, not a checker)


async def producer(queue, num_consumers):
    for i in range(5):
        print(f"Producing {i}")
        await queue.put(i)
        # queue.put_nowait(i)
        await asyncio.sleep(1)
    # Send one None sentinel per consumer so each consumer can exit
    for _ in range(num_consumers):
        await queue.put(None)


async def consumer(name, queue):
    while True:
        item = await queue.get()
        # item = queue.get_nowait()
        await asyncio.sleep(random.uniform(0.5, 2))

        if item is None:
            queue.task_done()  # None was put() so counter went up → must bring it down before break
            break  # task_done() must be BEFORE break, after break = unreachable

        print(f"{name} Consumed {item}")
        queue.task_done()  # every get() needs a matching task_done() → decrements counter


async def main():
    queue = asyncio.Queue()
    num_consumers = 3

    producer_task = asyncio.create_task(producer(queue, num_consumers))
    consumer_tasks = []
    for i in range(num_consumers):
        consumer_tasks.append(asyncio.create_task(consumer(str(i), queue)))

    await producer_task

    await queue.join()

    for task in consumer_tasks:
        await task


asyncio.run(main())


## asyncio.Lock
# Only one coroutine can hold the lock at a time
# Use: async with lock:
# count is an int (immutable) so we use a dict as shared mutable state


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

    print("Final count:", shared["count"])  # always 2, never a race condition


# asyncio.run(main())

#### FLOW
# main starts gather(task_1, task_2)

# → task_1 starts:
#     print("task_1: wants to update count")
#     async with lock:           ← lock is free, task_1 acquires it
#         current = shared["count"]   # reads 0
#         await asyncio.sleep()  ← yields control to event loop

# → task_2 starts:
#     print("task_2: wants to update count")
#     async with lock:           ← lock is TAKEN → task_2 suspends here, waiting

# → event loop has nothing else runnable, waits for task_1's sleep to finish

# → task_1 resumes:
#         shared["count"] = 0 + 1    # writes 1
#         print("task_1: count updated to 1")
#     ← lock released (exits async with)

# → task_2 wakes up, acquires lock:
#         current = shared["count"]   # reads 1
#         await asyncio.sleep()  ← yields control
#         shared["count"] = 1 + 1    # writes 2
#         print("task_2: count updated to 2")
#     ← lock released

# → gather finishes, back to main:
#     print("Final count: 2")


## asyncio.Semaphore -> act as rate limiter


async def fetch(url, sem):
    print("Trying to fetch url")
    async with sem:  # each coroutine tries to acquire — first 3 get in, rest wait
        print("Fetching URL", url)
        await asyncio.sleep(random.uniform(1, 3))


async def main():
    sem = asyncio.Semaphore(3)  # ← just the number, no mention of specific tasks
    urls = ["abc.com", "def.com", "ghi.com", "jkl.com", "mno.com", "pqr.com", "stu.com"]
    # create 10 tasks — semaphore automatically limits to 3 running at once
    tasks = [asyncio.create_task(fetch(url, sem)) for url in urls]
    await asyncio.gather(*tasks)
    print("All url fetched \n")


# asyncio.run(main())


## asyncio.Event
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
