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

