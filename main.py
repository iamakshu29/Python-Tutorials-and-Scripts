import asyncio

# async keyword when wrapped around a func, makes it a coroutine object
# await "may" pause this coroutine and give control back to the event loop, until the awaited operation is ready
# asyncio.run(func()) starts an event loop and run the coroutine


# def sync_func():
#     print("Synchronous fun is called")


# sync_func()


# async def async_func():
#     print("Asynchronous fun is called")


# asyncio.run(async_func())


# # Using await


async def task1():
    print("START")
    await asyncio.sleep(1)
    print("PAUSE")
    await asyncio.sleep(1)
    print("DONE")


async def task2():
    await task1()
    print("Task 2 done")


# asyncio.run(task1())
# asyncio.run(task2())


# returns a corouting object


async def hello():
    print("Hello")


async def main():
    x = hello()
    print(x)


# asyncio.run(main())


async def test_func_1():
    print("hi")
    await asyncio.sleep(1)
    print("bye")


async def test_func_2():
    print("hi again")
    await asyncio.sleep(1)
    print("bye again")


# this is not good pattern - as it create the new event loop everytime we run asyncio.run() , runs the coroutine and then close the event loop
# this is inefficient and not how async app are usually structured.
# asyncio.run(test_func_1())
# asyncio.run(test_func_2())


# this is correct pattern - as it only creates one event loop.
async def main():
    await test_func_1()
    await test_func_2()


# Even though the functions are async, you're still waiting for one to finish before starting the next.
# asyncio.run(main())


# Now we understand
# Sequential await vs Concurrent execution
# Sequential await - above code is an example of Sequential await.


# Now we move to create_task - Here, we learn what a Task object is and how background execution actually works.

# What is a Task?
# A Task is a wrapper around a coroutine that tells the event loop:
# "Schedule this coroutine to run independently."

# >> asyncio.create_task()


async def worker():
    print("worker start")
    await asyncio.sleep(3)
    print("worker end")


async def main():
    task = asyncio.create_task(
        worker()
    )  # worker() coroutine is now wrapped inside a task

    print("main continues")

    await task


# asyncio.run(main())


async def download():
    print("download started")
    await asyncio.sleep(5)
    # 2. This await again pause the corouting and sends control to the event loop
    print("download finished")


async def main():
    task = asyncio.create_task(download())
    # This creates a Task object and registers download() with the event loop.
    # At this point download() has not run yet, but it is ready to run as soon as the current coroutine (main) yields control back to the event loop.

    print("user can do other things")

    await asyncio.sleep(2)
    # 1. This await does exactly this - pauses this coroutine and give control back to the event loop.
    # so as soon as the control goes back to event loop the task is executed.

    print("still working")

    await task
    # try commenting it -> it will not wait for download() sleep to 5 second
    # and return only this
    # user can do other things
    # download started
    # still working


# await task -
# a. Wait for completion of download()
# b. Get the return value, if any
# c. Receive exceptions, if any


# asyncio.run(main())


# Another example
async def worker():
    print("worker start")
    await asyncio.sleep(3)
    print("worker done")


async def main():
    asyncio.create_task(worker())

    for i in range(3):
        print("main", i)
        await asyncio.sleep(1)


# if you dont understand, why the o/p comes as the way it is..Just focus on timing..because of timing only the O/P is like this
# change the for loop asynio timing to get different order in O/P
# asyncio.run(main())

# Instead of creating task, we can simply use gather and results (if any) are collected in a ordered list
# Running them concurrently - Start both tasks, then wait until all of them finish.
# For that,
# >> use asyncio.gather():

# Cons of using gather()
# Not optimal for error handling
# Will not cancel other coroutines if one them were to fail


async def main():
    await asyncio.gather(test_func_1(), test_func_2())


# asyncio.run(main())


# TaskGroup()
# Preferred way to create multiple tasks and organize them together, instead of creating each tasks manually or use the gather() func.
# As, it comes with built-in error handling
# And if any of the task in the taskgroup were to fail, it will automatically cancel all of other tasks


async def fetch(id, sleep_time):
    print(f"Coroutine {id} starting to fetch data.")
    await asyncio.sleep(sleep_time)
    return {"id": id, "data": f"Sample data from coroutine {id}"}


async def main():
    tasks = []

# async context manager
    async with asyncio.TaskGroup() as tg:
        for i, sleep_time in enumerate([2, 1, 3], start=1):
            task = tg.create_task(fetch(i, sleep_time))
            tasks.append(task)

    results = [task.result() for task in tasks]

    for result in results:
        print(f"Received result: {result}")


asyncio.run(main())



# Futures
# Just familiar with it, as it low level programming code


