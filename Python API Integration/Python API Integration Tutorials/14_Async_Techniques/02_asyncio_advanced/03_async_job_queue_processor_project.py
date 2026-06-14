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

async def producer(queue, num_consumers, event):
    print("Start producing Jobs")
    for job in jobs:
        await queue.put(job)
        await asyncio.sleep(random.uniform(0.5, 2))
    event.set()                      # Stretch Goal 3 --> signal once: all jobs queued, consumers can start 
    for _ in range(num_consumers):   # one None per consumer
        await queue.put(None)
    print("Producer done")

async def consumer(user_id, queue, sem, event):
    print(f"Consumer {user_id} started")
    while True:
        await event.wait() # Stretch Goal 3
        result = await queue.get()

        if result is None:           # sentinel → exit
            queue.task_done()        # None was put() so counter went up → must bring it down before break
            break                    # task_done() must be BEFORE break, after break = unreachable

        async with sem:              # semaphore only around job processing
            if result["type"] == "message": # Streatch Goal 1 --> Use a job with longer time
                print(f"Consumer {user_id} processing job {result['type']}")
                await asyncio.sleep(3)
                print(f"Consumer {user_id} done with job {result['type']}")
            else:
                print(f"Consumer {user_id} processing job {result['id']}")
                await asyncio.sleep(random.uniform(0.5, 2))
        # Streatch Goal 2 --> Max 2 retries 
                if random.random() < 0.3:   # Stretch Goal 2: 30% random failure chance
                    retries = result.get("retries", 0)
                    if retries < 2:
                        result["retries"] = retries + 1
                        print(f"Job {result['id']} failed → retry {result['retries']}/2, re-queuing")
                        await queue.put(result)  # put back for retry (counter goes up again)
                    else:
                        print(f"Job {result['id']} failed after 2 retries → dropping")
                else:
                    print(f"Consumer {user_id} done with job {result['id']}")

        queue.task_done()            # every get() needs a matching task_done() → decrements counter

## WHY semaphore inside the loop ?
# get job from queue   ← no semaphore, any consumer can grab jobs freely
# async with sem:      ← only 3 consumers can PROCESS at the same time and do the work

async def main():
    num_consumers = 4
    sem = asyncio.Semaphore(3)
    queue = asyncio.Queue()
    event = asyncio.Event()

    # start consumers concurrently WITH producer
    async with asyncio.TaskGroup() as tg:
        tg.create_task(producer(queue, num_consumers, event))
        for i in range(1, num_consumers + 1):
            tg.create_task(consumer(i, queue, sem, event))

    print("All jobs consumed")

asyncio.run(main())
    
# Stretch Goal 4 -> Already implemented with TaskGroup and None Pattern