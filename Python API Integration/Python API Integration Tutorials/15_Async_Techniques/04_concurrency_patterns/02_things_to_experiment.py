import asyncio
import time
import httpx
from concurrent.futures import ProcessPoolExecutor

# Run a CPU-heavy loop inside an async function — watch it block other coroutines
# Move the CPU-heavy loop to ProcessPoolExecutor (via loop.run_in_executor) — watch others run freely (true parallelism, bypasses GIL)

def cpu_heavy(n):
    print("CPU heavy task started")
    result = 0
    for i in range(n):
        result += i * i
    print("CPU heavy task Ended")
    return result

async def cpu_heavy_sequential(n):
    result= cpu_heavy(n)      # blocking sync call — blocks the event loop
    await asyncio.sleep(0.1)
    return result

async def cpu_heavy_processpool(n):
    # run_in_executor offloads cpu_heavy to a separate process — event loop stays free.
    # task_a and task_b will run concurrently while cpu_heavy runs in its own process.
    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor() as executor:
        await loop.run_in_executor(executor, cpu_heavy, 50_000_000)


async def task_a():
    print("task a started")
    await asyncio.sleep(1)
    print("task a ended")
    return "a"

async def task_b():
    print("task b started")
    await asyncio.sleep(1)
    print("task b ended")
    return "b"

async def cpu_blocking_routines():
    # Expected: task_a and task_b are completely frozen until cpu_heavy finishes.
    # You'll see no output from task_a or task_b until cpu_heavy completes.
    result = await asyncio.gather(cpu_heavy_sequential(50_000_000),task_a(),task_b())
    return result

async def cpu_running_parallely():
    # Expected: task_a and task_b run freely while cpu_heavy runs in a separate process.
    # You'll see task_a/task_b output interleaved with cpu_heavy start/end.
    result = await asyncio.gather(cpu_heavy_processpool(50_000_000),task_a(),task_b())
    return result


# if __name__ == "__main__":
#     # Run a CPU-heavy loop inside an async function — watch it block other coroutines
#     print("=== POINT 1: CPU-heavy blocks event loop ===")
#     asyncio.run(cpu_blocking_routines())
#     print("=== Done ===")

#     print()

#     # Move the CPU-heavy loop to ProcessPoolExecutor (via loop.run_in_executor) — watch others run freely (true parallelism, bypasses GIL)
#     print("=== POINT 2: CPU-heavy in ProcessPoolExecutor — event loop stays free ===")
#     asyncio.run(cpu_running_parallely())
#     print("=== Done ===")


# as_completed with httpbin delays: send requests with delays [3,1,2,1,3]

async def fetch_url(client, URL, delay):
    try:
        response = await client.get(f"{URL}/{delay}")
        # delay is part of the URL path — httpbin waits that many seconds before responding.
        # Requests with delay=1 finish first, delay=3 finish last regardless of submission order.
        response.raise_for_status()
        print(response.json())
    except httpx.HTTPStatusError as e:
        print(f"HTTP Error: {e.response.status_code}")
        print(e.response.text)

    except httpx.RequestError as e:
        print(f"Request failed: {e}")

    except Exception as e:
        print(f"Unexpected error: {e}")

async def main():
    URL = "https://httpbin.io/delay"
    delays = [3,1,2,1,3]
    async with httpx.AsyncClient() as client:
        coros = [fetch_url(client, URL, delay) for delay in delays]
        # as_completed yields futures in COMPLETION ORDER, not submission order.
        # Fastest requests (delay=1) come back first even though they weren't first in the list.
        for future in asyncio.as_completed(coros):
            res = await future
            print(f"Got result: {res!r}")

# asyncio.run(main()) # results should come back in order: 1,1,2,3,3 not 3,1,2,1,3



# Build a token bucket with a very low refill rate and watch requests get throttled

async def refill_tokens(lock, token_count):
    # 10s refill (vs 2s in the learning file) — extreme throttle to make rejection obvious.
    # Tokens all arrive at ~10s; requests start immediately — most see an empty bucket.
    await asyncio.sleep(10)
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

    # Key difference from the learning file: requests are created BEFORE tokens are ready.
    # Both token creation and requests run concurrently — requests arrive when bucket is empty.
    sending_request = [asyncio.create_task(hit_request(lock,token_count,req)) for req in range(1,12)]

    await asyncio.gather(*create_token)
    print("Token created",token_count["count"])
    await asyncio.gather(*sending_request)

# asyncio.run(main())