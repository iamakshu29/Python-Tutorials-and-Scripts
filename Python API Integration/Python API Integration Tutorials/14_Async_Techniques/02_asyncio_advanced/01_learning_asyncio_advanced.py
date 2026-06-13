import asyncio
import time

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

### To inspect the outcome of a completed asyncio.Task
# task.result() ->
# Returns the value returned by the coroutine.
# raises asyncio.CancelledError for a cancelled task

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

# For gather we dont need to explicit await
# For task we need an explicit await, to get the return values or anything
# For TaskGroup also, we donot require an explicit await.


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
# Shield() protects us against
# It protects against cancellation propagation from the awaiting or child coroutine.
# If the coroutine doing the await is cancelled, the cancellation stops at the shield boundary. The awaited task keeps running.

# shield() does NOT protect against
# The cancellation requested directly to the task itself. The task will still receive CancelledError and can end in the cancelled state.

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


async def producer(queue):
    for i in range(5):
        print(f"Producing {i}")
        await queue.put(i)
        # queue.put_nowait(i)
        await asyncio.sleep(1)
    await queue.put(None)


import random


async def consumer(name, queue):
    while True:
        item = await queue.get()
        # item = queue.get_nowait()
        await asyncio.sleep(random.uniform(0.5, 2))

        if item is None:
            queue.task_done()
            break

        print(f"{name} Consumed {item}")
        queue.task_done()


async def main():
    queue = asyncio.Queue()

    producer_task = asyncio.create_task(producer(queue))
    consumer_task_1 = asyncio.create_task(consumer("1", queue))
    consumer_task_2 = asyncio.create_task(consumer("2", queue))
    consumer_task_3 = asyncio.create_task(consumer("3", queue))

    await producer_task
    await queue.join()
    await consumer_task_1
    await consumer_task_2
    await consumer_task_3


asyncio.run(main())
