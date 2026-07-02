import asyncio
import time
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor


# ================================================================================
# CONCEPT 2 — asyncio + ThreadPoolExecutor
# ================================================================================
# Goal: show that calling a blocking (sync) function directly inside async code
# freezes the ENTIRE event loop — no other coroutine can run.
# Fix: offload it to a thread using asyncio.to_thread() so the event loop stays free.
#
# time.sleep() here represents any blocking library you can't change
# (e.g. psycopg2.connect(), requests.get(), legacy SDK calls).
# You can't just replace those with asyncio.sleep — they're not yours to modify.


async def the_blocker():
    # Calls time.sleep DIRECTLY inside async code.
    # time.sleep holds the GIL and never yields — the event loop is completely frozen.
    # the_victim() will not get a single turn while this runs.
    print("[Blocker] Starting time.sleep(5) directly...")
    time.sleep(5)
    print("[Blocker] Done")


async def the_victim():
    # In the blocking demo: silent for 5s (frozen by the_blocker). In the non-blocking demo: prints freely every second.
    for i in range(7):
        print(f"  [Victim] I'm alive at t={i}s")
        await asyncio.sleep(1)


async def the_blocker_fixed():
    # asyncio.to_thread() runs time.sleep in a worker thread from the default ThreadPoolExecutor.
    # The event loop thread is FREE while the worker thread blocks.
    # Key: the function itself is still sync — to_thread just moves it off the event loop thread.
    print("[Blocker] Starting time.sleep(5) via to_thread...")
    await asyncio.to_thread(time.sleep, 5)
    print("[Blocker] Done")


async def demo_c2_blocking():
    # Expected output: victim prints NOTHING until blocker finishes at t=5s.
    print("=== CONCEPT 2: BLOCKING (direct time.sleep call) ===")
    await asyncio.gather(the_blocker(), the_victim())


async def demo_c2_non_blocking():
    # Expected output: victim prints at t=0,1,2,3,4 WHILE blocker sleeps.
    print("=== CONCEPT 2: NON-BLOCKING (asyncio.to_thread) ===")
    await asyncio.gather(the_blocker_fixed(), the_victim())


# ================================================================================
# CONCEPT 3 — asyncio + ProcessPoolExecutor
# ================================================================================
# Goal: show TRUE parallelism for CPU-bound work.
# cpu_heavy() is a pure Python math loop — it never releases the GIL.
# Threads would NOT help (GIL blocks them). Processes each have their own GIL.
#
# The key lesson here is SPEED (timing), not blocking:
#   - Sequential: 3 tasks × N seconds = 3N seconds total
#   - Parallel:   3 tasks run on 3 CPU cores simultaneously ≈ N seconds total
#
# NOTE (Windows): ProcessPoolExecutor spawns child processes by re-importing
# the script. Without if __name__ == "__main__", it crashes in an infinite loop.
# Always guard asyncio.run() with that check on Windows.
#
# NOTE (overhead): process startup + pickling has cost (~0.5–1s on Windows).
# Use at least 50_000_000 iterations so the CPU work dominates the overhead.
# For small tasks, the overhead makes parallel SLOWER — that's expected.

def cpu_heavy(n):
    # Pure Python computation — never releases the GIL.
    result = 0

    for i in range(n):
        result += i * i
        
    return result


async def demo_c3_sequential():
    start = time.perf_counter()

    cpu_heavy(50_000_000)
    cpu_heavy(50_000_000)
    cpu_heavy(50_000_000)
    
    print(f"Sequential: {time.perf_counter() - start:.2f}s")


async def demo_c3_parallel():
    # Runs 3 cpu_heavy calls in 3 SEPARATE PROCESSES simultaneously.
    # Each process has its own GIL — true parallel execution on separate CPU cores.
    # Total time ≈ time_for_one_call (all 3 overlap).
    #
    # run_in_executor(executor, func, arg):
    #   - executor: the ProcessPoolExecutor (manages child processes)
    #   - func: sync function to run (no parentheses — pass the reference)
    #   - arg: argument passed to func after pickling through OS pipe
    #
    # context manager handles process pool startup and cleanup automatically.
    loop = asyncio.get_running_loop()

    start = time.perf_counter()

    with concurrent.futures.ProcessPoolExecutor() as executor:
        await asyncio.gather(
            loop.run_in_executor(executor, cpu_heavy, 50_000_000),
            loop.run_in_executor(executor, cpu_heavy, 50_000_000),
            loop.run_in_executor(executor, cpu_heavy, 50_000_000),
        )

    print(f"Parallel:   {time.perf_counter() - start:.2f}s")




# NOTE: This is the SAME concept 2 pattern (blocker + victim) applied to concept 3.
# Concept 2 used time.sleep (I/O-bound) offloaded via asyncio.to_thread.
# Here we use cpu_heavy (CPU-bound) offloaded via ProcessPoolExecutor.
#   asyncio.to_thread        → good for blocking I/O (same process, thread)
#   run_in_executor(Process) → good for CPU-bound work (separate process)

async def cpu_blocker(n):
    print("[CPU Blocker] Running cpu_heavy directly on event loop...")
    result = cpu_heavy(n)
    print("[CPU Blocker] Done")
    
    return result

async def cpu_blocker_fixed(n):
    print("[CPU Blocker] Running cpu_heavy via ProcessPoolExecutor...")
    
    loop = asyncio.get_running_loop()
    
    with ProcessPoolExecutor() as executor:
        result = await loop.run_in_executor(executor, cpu_heavy, n)

    print("[CPU Blocker] Done")
    
    return result

async def demo_c3_blocking():
    print("=== CONCEPT 3: BLOCKING (cpu_heavy direct call) ===")
    await asyncio.gather(cpu_blocker(10_000_000), the_victim())

async def demo_c3_non_blocking():
    print("=== CONCEPT 3: NON-BLOCKING (cpu_heavy via ProcessPoolExecutor) ===")
    await asyncio.gather(cpu_blocker_fixed(10_000_000), the_victim())

# if __name__ == "__main__":
#     # --- Concept 2: I/O-bound blocking (time.sleep) ---
#     asyncio.run(demo_c2_blocking())
#     print()
#     asyncio.run(demo_c2_non_blocking())
#     print()

#     # --- Concept 3A: CPU-bound timing (sequential vs parallel speed) ---
#     asyncio.run(demo_c3_sequential())
#     asyncio.run(demo_c3_parallel())
#     print()

#     # --- Concept 3B: CPU-bound blocking (same blocker+victim pattern as concept 2) ---
#     asyncio.run(demo_c3_blocking())
#     print()
#     asyncio.run(demo_c3_non_blocking())


# ================================================================================
# CONCEPT 4 — asyncio.gather vs asyncio.wait
# ================================================================================
# Goal: show the difference between gather (collect all results) and
# wait (react to tasks as they finish, with control over when to stop).
#
# gather:  returns a list of results in INPUT ORDER, only after ALL tasks finish.
#          raises immediately if any task raises (unless return_exceptions=True).
#
# wait:    returns (done, pending) sets.
#          done    → tasks that finished — safe to call .result() on.
#          pending → tasks still running — calling .result() raises InvalidStateError.
#
# return_when flags:
#   ALL_COMPLETED   → wait for every task (default)
#   FIRST_COMPLETED → return as soon as any ONE task finishes
#   FIRST_EXCEPTION → return as soon as any ONE task raises
#
# What to do with pending:
#   Cancel:      for task in pending: task.cancel()
#   Await later: done2, _ = await asyncio.wait(pending)

async def task_a():
    print("task a started")
    await asyncio.sleep(1)
    print("task a ended")
    return "a"

async def task_b():
    print("task b started")
    await asyncio.sleep(5)
    print("task b ended")
    return "b"

async def demo_gather():
    # Waits for BOTH tasks, returns ["a", "b"] in input order.
    return await asyncio.gather(task_a(), task_b())

async def demo_wait():
    # Must wrap coroutines in create_task — wait() requires Task objects, not bare coroutines.
    tasks = [
        asyncio.create_task(task_a()),
        asyncio.create_task(task_b())
    ]
    # FIRST_COMPLETED: returns as soon as task_a finishes (1s).
    # done = {task_a}, pending = {task_b} (still running — do NOT call .result() on pending).
    # Try ALL_COMPLETED to see both tasks finish before returning.
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    for task in done:
        print("Wait results", task.result())

async def main():
    await demo_wait()
    return await demo_gather()

# print(asyncio.run(main()))

# ================================================================================
# CONCEPT 5 — asyncio.as_completed()
# ================================================================================
# Goal: process results as each task finishes — fastest first, not input order.
#
# as_completed() starts ALL coroutines concurrently and returns an iterator
# of futures. Each iteration yields the NEXT future that completes.
#
# You still need to await each future — as_completed gives you a HANDLE, not
# the result. await future pauses until that specific task is done, then
# gives the value.
#
# vs gather:  gather waits for ALL (5s total), then gives ["a", "b"] together.
#             as_completed gives "a" at t=1s, then "b" at t=5s — process early.
#
# When to use: fetching multiple URLs, showing results as they arrive instead
#              of waiting for the slowest one before displaying anything.

async def demo_as_compelted():
    coros = [task_a(), task_b()]
    result = []
    for future in asyncio.as_completed(coros):
        # All coroutines are already running concurrently.
        # await here pauses until THIS specific future finishes — not all of them.
        # Order of results = completion order: "a" arrives at t=1s, "b" at t=5s.
        res = await future
        print(f"Got result: {res!r}")
        result.append(res)
    return result

# print(asyncio.run(demo_as_compelted()))
# asyncio.run(demo_as_compelted())

# ================================================================================
# CONCEPT 6 — Rate limiting patterns
# ================================================================================

# Pattern 1 — Semaphore
# ================================================================================

start = time.perf_counter()

def log(msg):
    print(f"{time.perf_counter() - start:.1f}s | {msg}")

async def db_connect(semaphore,db):
    async with semaphore:
        log(f"Querying {db}")
        await asyncio.sleep(3)
        log(f"Connected {db}")

async def main():
    semaphore = asyncio.Semaphore(3)

    db_pool = ["paymentDB","imageDB","cartDB","passwordDB","usernameDB","servicesDB","applicationsDB","middlewareDB"]
    tasks = [asyncio.create_task(db_connect(semaphore,db)) for db in db_pool]
    
    await asyncio.gather(*tasks)

# asyncio.run(main())


# Pattern 2 — Token Bucket
# ================================================================================

# Finite Tokens bucket
# ================================================================================

async def refill_tokens(lock, token_count):
    await asyncio.sleep(2)
    async with lock:
        token_count["count"] += 1

async def hit_request(lock, token_count, req):
    print("Sending request: ", req)
    await asyncio.sleep(1)
    try:
        async with lock:
            if token_count["count"] > 0:
                print("Request Sent successfully")
                token_count["count"] -= 1
                print(f"balance remaining: {token_count["count"]}")
            else:
                raise ValueError
    except ValueError as e:
        print("All tokens Exhausted, unable to sent request")

async def main():
    lock = asyncio.Lock()
    token_count = {"count": 0}
    token_to_create = 10

    create_token = [asyncio.create_task(refill_tokens(lock,token_count)) for _ in range(token_to_create)]

    await asyncio.gather(*create_token)
    print("Token created",token_count["count"])
    sending_request = [asyncio.create_task(hit_request(lock,token_count,req)) for req in range(1,12)]

    await asyncio.gather(*sending_request)

# asyncio.run(main())


# Infinite Tokens Bucket
# ================================================================================

# - Token will keep on increasing at rate for 1 sec. We are not awaiting the result as the tokens are creating as infinteloop. So let the tokens create in background only.

async def refill_tokens_indefinitely(lock, token_count, token_to_create):
    while True:
        await asyncio.sleep(1)

        async with lock:
            if token_count["count"] < token_to_create:
                token_count["count"] += 1

async def hit_request_with_retry(lock, token_count, req):
    print("Sending request: ", req)
    await asyncio.sleep(1)
    try:
        async with lock:
            if token_count["count"] > 0:
                print("Request Sent successfully")
                token_count["count"] -= 1
                print(f"balance remaining: {token_count["count"]}")
        await asyncio.sleep(20)
        async with lock:
            print("Trying again")
            print(f"balance remaining: {token_count["count"]}")
            if token_count["count"] > 0:
                print("Request Sent successfully")
                token_count["count"] -= 1
                print(f"balance remaining: {token_count["count"]}")
    except ValueError as e:
        print("All tokens Exhausted, unable to sent request")


async def main():
    lock = asyncio.Lock()
    token_count = {"count": 0}
    token_to_create = 10
    request_to_send = 15

    create_token = asyncio.create_task(refill_tokens_indefinitely(lock,token_count, token_to_create))

    sending_request = [asyncio.create_task(hit_request_with_retry(lock,token_count,req)) for req in range(1,request_to_send)]

    await asyncio.gather(*sending_request)

# asyncio.run(main())



# Pattern 3 — asyncio.sleep
# ================================================================================

async def task(i):
    print(f"task {i} started")
    await asyncio.sleep(1)
    print(f"task {i} ended")

async def rate_limiting_sleep_pattern():
    rate_limit = 3

    count = 0
    results = []
    for i in range(10):
        if count >= rate_limit:
            await asyncio.sleep(4)
            count = 0
        results.append(asyncio.create_task(task(i)))
        count += 1

    for i in range(len(results)):
        await results[i]

async def main():
    await rate_limiting_sleep_pattern()

# asyncio.run(main())


# ================================================================================
# CONCEPT 7 — Producer-consumer with backpressure
# ================================================================================
# Producer is faster than consumers → queue fills to maxsize=12 → await queue.put(i) blocks the producer — that's backpressure actually triggering.
async def fast_producer(queue, num_of_msg, consumer_size):
    for i in range(num_of_msg):
        print(f"Producing {i}")
        await queue.put(i)
        await asyncio.sleep(1)
    for _ in range(consumer_size):
        await queue.put(None)
        

async def slow_consumer(queue, consumer_name):
    while True:
        msg = await queue.get()
        if msg is None:
            queue.task_done()
            print(f"Consumer {consumer_name} exiting")
            break
        else:
            print(f"Consumer {consumer_name} Processing message {msg}")
            await asyncio.sleep(5)
            print(f"Message {msg} processed")
            queue.task_done()


async def main():
    queue = asyncio.Queue(maxsize=12)
    consumers = ["web","app"]
    num_of_msg = 20

    producer_task = asyncio.create_task(fast_producer(queue,num_of_msg,len(consumers)))
    

    consumer_tasks = [asyncio.create_task(slow_consumer(queue, consumer)) for consumer in consumers]
    
    await producer_task
    
    # await asyncio.gather(*consumer_tasks)
# Instead of awaiting we use queue.join() method. as it also waits for all the message to get processed
## check 01_learning_asyncio_advanced.py -> queue section for better understanding

    await queue.join()


# asyncio.run(main())

# ================================================================================
# CONCEPT 8 — Circuit breaker pattern (conceptual + implementation)
# ================================================================================
##### Implemented in another File name 08_circuit_breaker.py #####

