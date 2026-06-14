import asyncio
import time


async def func1():
    return "func1 is executed"


# 1.
# func1()  # Getting RuntimeWarning: coroutine 'func1' was never awaited

# 2.
# print(asyncio.run(func1()))


async def func2():
    print("Before Yield")
    await asyncio.sleep(1)
    print("After Yield")


# 3.
# await asyncio.sleep(1) suspends the coroutine and yields control to the event loop.
# The event loop runs other ready tasks/"coroutines" while this coroutine is waiting.
# After at least 1 second has elapsed, the event loop marks this coroutine as ready to run again.
# When the event loop schedules it, execution resumes

# asyncio.run(func2())


# 4. Coroutine chaining OR Sequential Working...though the function as async but they still behaves like sync. Tasks are done one after the other not concurrently
async def parse_response():
    print("Parsing Starts")
    await asyncio.sleep(2)
    print("Parsing Done")


async def fetch_parsed_data():
    print("Fetching Starts")
    await asyncio.sleep(2)
    print("Fetching Done")


async def main():
    await parse_response()
    await fetch_parsed_data()


# asyncio.run(main())


# 5. asyncio.gather() - To run tasks asynchronously, Func executes in order
async def parse_response_2():
    await asyncio.sleep(2)
    return "Data Parsing Done Successfully"


async def fetch_parsed_data_2():
    await asyncio.sleep(2)
    return "Data Fetching Done Successfully"


# Time with gather
async def main():
    start = time.perf_counter()
    result = await asyncio.gather(parse_response_2(), fetch_parsed_data_2())
    end = time.perf_counter()
    print(f"Time taken with gather: {end - start:.2f} seconds")
    return result


# print(asyncio.run(main()))


# Time without gather
async def main():
    result = []
    start = time.perf_counter()
    result.append(await parse_response_2())
    result.append(await fetch_parsed_data_2())
    end = time.perf_counter()
    print(f"Time taken without gather: {end - start:.2f} seconds")
    return result


# print(asyncio.run(main()))

# 6. asyncio.create_task() - so that the async func run independently


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
    task1 = asyncio.create_task(parse_response_3())
    task2 = asyncio.create_task(fetch_parsed_data_3())
    result = []
    # Uncomment and execute, you will see the change in time, because it waits for yielding time to return the output
    # result.append(await task1)
    # result.append(await task2)
    end = time.perf_counter()

    print(f"Time taken without gather: {end - start:.2f} seconds")
    print("Both Functions Completed")

    return result


print(asyncio.run(main()))

# 7. Timing and understanding the event loop - Used all along


#### Things to experiment with, Creating Errors and Print their Output ####
# a. Call an async function without await — what happens?
async def exp_1():
    return


# exp_1()
# Response - Getting RuntimeWarning: coroutine 'exp_1' was never awaited


# b. Use time.sleep() inside an async function — what does it do to other coroutines?


async def exp_2():
    time.sleep(2)
    print("exp_2")


async def exp_3():
    await asyncio.sleep(1)
    print("exp_3")


async def main():
    await asyncio.gather(exp_2(), exp_3())
    print("main")


# asyncio.run(main())
# Response - Even Concurrent Function run as Synchronous Function

# c. What happens if you raise an exception inside a gather?


async def task1():
    await asyncio.sleep(1)
    print("task1 completed")
    return 1


async def task2():
    await asyncio.sleep(0.5)
    raise ValueError("Something went wrong in task2")


async def task3():
    await asyncio.sleep(2)
    print("task3 completed")
    # return 3


async def main():
    try:
        results = await asyncio.gather(
            task1(), task2(), task3(), return_exceptions=False
        )
        print(results)
    except Exception as e:
        print(f"Caught exception: {e}")


# asyncio.run(main())

# Response
# By default return_exceptions=False
# The first exception raised is immediately propagated and re-raised when awaiting gather()
# Other Tasks continue running Background until completed or cancelled. (based on timing)

# Use, return_exceptions=True -> return list of coroutine which contains values as the return values
# If you want all tasks to finish and collect exceptions as results list instead of being raised.

# d. What is the return value of a coroutine that has no return statement?
# Response = None
