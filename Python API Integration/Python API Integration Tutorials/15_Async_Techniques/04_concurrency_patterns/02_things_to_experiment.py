import time
import asyncio

start_time = time.time()

def log(msg):
    elapsed = time.time() - start_time
    print(f"[{elapsed:.3f}s] {msg}")

# Run a CPU-heavy loop inside an async function — watch it block other coroutines
async def cpu_heavy(n):
    # Pure Python computation — never releases the GIL.
    result = 0

    log("Computation Starts")
    for i in range(n):
        result += i * i
    await asyncio.sleep(0.1)
    log("Computation Ends")
    return result

async def task_a():
    log("task a started")
    await asyncio.sleep(1)
    log("task a ended")
    return "a"

async def task_b():
    log("task b started")
    await asyncio.sleep(1)
    log("task b ended")
    return "b"


async def main():
    result = await asyncio.gather(cpu_heavy(50_000_000),task_a(),task_b())
    return result

print(asyncio.run(main()))



