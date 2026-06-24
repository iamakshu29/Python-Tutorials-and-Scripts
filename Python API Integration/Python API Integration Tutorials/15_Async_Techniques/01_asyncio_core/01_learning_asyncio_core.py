# 01_learning_asyncio_core.py — Core asyncio Concepts & Event Loop Behavior

# =============================================
# KEY CONCEPTS
# =============================================
# - asyncio.run() is not what makes code concurrent — it just runs the top-level coroutine
# - To get concurrency, coroutines must be SCHEDULED before awaiting (via create_task / gather)
# - Async ≠ Concurrent: async functions still run sequentially if awaited one-by-one
# - An async function can pause (await) and yield control back to the event loop
# - Sync code can achieve concurrency via: Threads (threading), Processes (multiprocessing)

import asyncio
import time


# =============================================
# 1. Calling a Coroutine Without await
# =============================================
# An async function returns a coroutine object — it does NOT execute on its own.
# You must either await it or schedule it via asyncio.run() / create_task() / gather().
async def func1():
    return "func1 is executed"


# func1()  # RuntimeWarning: coroutine 'func1' was never awaited

# asyncio.run() effectively awaits the top-level coroutine for you — no explicit await needed
# print(asyncio.run(func1()))


# =============================================
# 2. await asyncio.sleep() — Yielding Control
# =============================================
# await suspends the coroutine and hands control back to the event loop.
# The event loop can then run other ready coroutines during the wait.
# Once the sleep duration passes, this coroutine is marked ready and resumes.
async def func2():
    print("Before Yield")
    await asyncio.sleep(1)  # Pauses here — event loop runs other tasks while waiting
    print("After Yield")


# asyncio.run(func2())


# =============================================
# 3. Coroutine Chaining — Sequential Execution
# =============================================
# Even though these are async functions, awaiting them one-by-one is still sequential.
# Each coroutine fully completes before the next one starts.
# To get concurrency, coroutines must be scheduled first — done via gather() or create_task().
async def parse_response():
    print("Parsing Starts")
    await asyncio.sleep(2)
    print("Parsing Done")


async def fetch_parsed_data():
    print("Fetching Starts")
    await asyncio.sleep(2)
    print("Fetching Done")


async def main():
    await parse_response()     # Waits for full completion before moving to the next line
    await fetch_parsed_data()  # Only starts after parse_response finishes — sequential, not concurrent


# asyncio.run(main())


# =============================================
# 4. asyncio.gather() — Concurrent Execution
# =============================================
# gather() schedules all coroutines at once so they run concurrently on the event loop.
# Total time ≈ max(individual times) instead of sum — both sleep(2) finish in ~2s, not ~4s.
# Results are returned in the same order as the coroutines were passed in.
async def parse_response_2():
    await asyncio.sleep(2)
    return "Data Parsing Done Successfully"


async def fetch_parsed_data_2():
    await asyncio.sleep(2)
    return "Data Fetching Done Successfully"


# With gather — concurrent, takes ~2s total
async def main():
    start = time.perf_counter()
    result = await asyncio.gather(parse_response_2(), fetch_parsed_data_2())  # Both start immediately
    end = time.perf_counter()
    print(f"Time taken with gather: {end - start:.2f} seconds")
    return result


# print(asyncio.run(main()))


# Without gather — sequential, takes ~4s total
async def main():
    result = []
    start = time.perf_counter()
    result.append(await parse_response_2())   # Fully completes before the next line runs
    result.append(await fetch_parsed_data_2())
    end = time.perf_counter()
    print(f"Time taken without gather: {end - start:.2f} seconds")
    return result


# print(asyncio.run(main()))

# =============================================
# 5. asyncio.create_task() — Independent Scheduled Tasks
# =============================================
# create_task() wraps a coroutine in a Task and schedules it on the event loop immediately.
# Unlike gather(), you get a Task object back that you can await later or leave running.
# Tasks start executing as soon as the event loop gets its next chance (next await point).
async def parse_response_3():
    print("Testing Parse response")
    await asyncio.sleep(2)
    return "Data Parsing Done Successfully"


async def fetch_parsed_data_3():
    print("Testing Fetch response")
    await asyncio.sleep(2)
    return "Data Fetching Done Successfully"


async def main():
    start = time.perf_counter()
    task1 = asyncio.create_task(parse_response_3())   # Scheduled immediately, starts on next await
    task2 = asyncio.create_task(fetch_parsed_data_3())  # Also scheduled — both run concurrently
    result = []
    # Awaiting here retrieves each task's result — both have been running concurrently since creation
    # result.append(await task1)
    # result.append(await task2)
    end = time.perf_counter()

    print(f"Time taken without gather: {end - start:.2f} seconds")
    print("Both Functions Completed")

    return result


# print(asyncio.run(main()))

# =============================================
# 6. Timing and the Event Loop
# =============================================
# The event loop is the scheduler — it decides which coroutine runs next.
# It picks the next ready coroutine whenever the current one yields via await.
# Understanding await timing helps predict resume order and total execution time.


# =============================================
# EXPERIMENTS — Expected Errors & Behavior
# =============================================

# =============================================
# EXP A: Coroutine Called Without await
# =============================================
# Calling an async function without await just creates a coroutine object — nothing runs.
async def exp_1():
    return


# exp_1()
# Result: RuntimeWarning: coroutine 'exp_1' was never awaited


# =============================================
# EXP B: time.sleep() Inside an Async Function
# =============================================
# time.sleep() is a blocking call — it freezes the entire thread, not just the coroutine.
# The event loop cannot run any other coroutines while the thread is blocked.


async def exp_2():
    time.sleep(2)          # BLOCKS the entire event loop — no other coroutine can run during this
    print("exp_2")


async def exp_3():
    await asyncio.sleep(1)  # Non-blocking — yields control, other coroutines can run
    print("exp_3")


async def main():
    await asyncio.gather(exp_2(), exp_3())
    print("main")


# asyncio.run(main())
# Result: Even concurrent functions behave synchronously because of time.sleep()

# =============================================
# EXP C: Exception Inside asyncio.gather()
# =============================================
# Default return_exceptions=False: the first exception propagates up and gather() stops.
# Other tasks that already started may still run until their next yield point.


async def task1():
    await asyncio.sleep(1)
    print("task1 completed")
    return 1


async def task2():
    await asyncio.sleep(0.5)
    raise ValueError("Something went wrong in task2")  # Raised before task1 and task3 finish


async def task3():
    await asyncio.sleep(2)
    print("task3 completed")
    # return 3


async def main():
    try:
        results = await asyncio.gather(
            task1(), task2(), task3(),
            return_exceptions=False  # Default — first exception is re-raised immediately
        )
        print(results)
    except Exception as e:
        print(f"Caught exception: {e}")


# asyncio.run(main())

# Result:
# task2's exception propagates immediately when gather() is awaited
# task1 and task3 continue running in the background until their next yield or completion
# Use return_exceptions=True to capture all exceptions as values instead of raising

# Use, return_exceptions=True -> return list of coroutine which contains values as the return values
# make it True, If you want all tasks to finish and collect exceptions as results list instead of being raised.

# d. What is the return value of a coroutine that has no return statement?
# Response = None
