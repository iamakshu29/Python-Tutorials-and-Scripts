import asyncio
import random


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

async def producer(queue, num_consumers):
    print("Start producing Jobs")
    for job in jobs:
        await queue.put(job)
        await asyncio.sleep(random.uniform(1, 3))
    for _ in range(num_consumers):   # one None per consumer
        await queue.put(None)
    print("Producer done")

async def consumer(user_id, queue, sem):
    print(f"Consumer {user_id} started")
    while True:
        result = await queue.get()

        if result is None:           # sentinel → exit
            queue.task_done()        # None was put() so counter went up → must bring it down before break
            break                    # task_done() must be BEFORE break, after break = unreachable

        async with sem:              # semaphore only around job processing
            print(f"Consumer {user_id} processing job {result['id']}")
            await asyncio.sleep(random.uniform(1, 3))
            print(f"Consumer {user_id} done with job {result['id']}")

        queue.task_done()            # every get() needs a matching task_done() → decrements counter

## WHY semaphore inside the loop ?
# get job from queue   ← no semaphore, any consumer can grab jobs freely
# async with sem:      ← only 3 consumers can PROCESS at the same time and do the work

async def main():
    num_consumers = 4
    sem = asyncio.Semaphore(3)
    queue = asyncio.Queue()

    # start consumers concurrently WITH producer
    async with asyncio.TaskGroup() as tg:
        tg.create_task(producer(queue, num_consumers))
        for i in range(1, num_consumers + 1):
            tg.create_task(consumer(i, queue, sem))

    print("All jobs consumed")

asyncio.run(main())
    