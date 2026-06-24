# 02_async_task_runner_project.py — Concurrent Task Runner with Race Conditions & Error Handling

# =============================================
# PROJECT OVERVIEW
# =============================================
# Simulates a real-world async pipeline: fetching users, processing orders, sending emails,
# and generating reports — all running concurrently via asyncio.gather().
# Demonstrates: task dependencies, exception handling in gather, and race conditions.

import asyncio
import time

count = 0


# =============================================
# ASYNC TASK DEFINITIONS
# =============================================
# Each coroutine simulates a real I/O-bound job (DB query, cart processing, email dispatch).
# asyncio.sleep() mimics the wait time for that operation.
async def fetch_users():
    print("Fetching Users from DB")
    await asyncio.sleep(3)
    print("Users Fetched Successfully")


async def process_orders():
    print("Process Orders from Cart")
    await asyncio.sleep(2)
    print("Orders Processed Successfully")


async def send_emails():
    print("Send Email to Users on Gmail")
    await asyncio.sleep(1)
    print("Emails sent Successfully")


async def generate_report():
    await fetch_users()  # Stretch goal req 1: dependency — report needs users fetched first
    print("Generating Users Report using Excel")
    await asyncio.sleep(4)
    print("Report Generated Successfully")
    raise ValueError(
        "Something went wrong"
    )  # Stretch goal req 2: simulate a failed job inside gather()


# =============================================
# STRETCH GOAL: Race Condition Demonstration
# =============================================
# Race condition occurs when multiple coroutines READ a shared value, yield, then all WRITE
# the same stale value — resulting in lost updates.
# Fix: move the yield (await) BEFORE the read so each coroutine sees the latest value.
# NOTE: This only works here by coincidence of timing — the real fix is asyncio.Lock() (Module 2).

# because of stretch goal requirement 3 - show race conditions
async def number_of_reports_generated_race_condition():
    global count
    temp = count  # READ — all three read before anyone writes
    await asyncio.sleep(1)  # YIELD — gap between read and write
    count = temp + 1  # WRITE — all three write 0+1=1 (lost updates)
    print(f"reports generated when race condition exists {count}")


async def number_of_reports_generated_race_condition_resolved():
    global count
    await asyncio.sleep(1)  # YIELD first — ensures read happens after prior writes settle
    temp = count  # READ — picks up the latest value after yielding
    count = temp + 1  # WRITE — increments correctly in this specific case
    print(f"reports generated after race conditions resolved {count}")


# NOTE: Moving await before the read is NOT a true fix for race conditions.
# It avoids the issue only due to this specific sleep duration and coroutine count.
# A different timing or more coroutines would break this assumption.
# The correct solution is asyncio.Lock() — covered in Module 2.


# =============================================
# CONCURRENT EXECUTION — All Tasks at Once
# =============================================
# gather() schedules all coroutines simultaneously — total time ≈ longest single task.
# return_exceptions=True means exceptions are captured as values, not raised — all tasks finish.
async def concurrent_execution():
    try:
        start = time.perf_counter()

        result = await asyncio.gather(
            process_orders(),
            send_emails(),
            generate_report(),
            number_of_reports_generated_race_condition(),
            number_of_reports_generated_race_condition(),
            number_of_reports_generated_race_condition(),
            number_of_reports_generated_race_condition_resolved(),
            number_of_reports_generated_race_condition_resolved(),
            number_of_reports_generated_race_condition_resolved(),
            return_exceptions=True,  # Exceptions returned as values — doesn't stop other tasks
        )

        end = time.perf_counter()

        print(f"\nTime taken by concurrent_execution: {end - start:.2f} seconds\n")
        return result
    except Exception as e:
        print(f"Caught exception: {e}")


# =============================================
# SEQUENTIAL EXECUTION — One Task at a Time
# =============================================
# Each coroutine is awaited individually — total time = sum of all task durations.
# Used here as a comparison to show the time savings from concurrent execution.
async def sequential_execution():
    try:
        start = time.perf_counter()

        await process_orders()
        await send_emails()
        await number_of_reports_generated_race_condition()
        await number_of_reports_generated_race_condition()
        await number_of_reports_generated_race_condition()
        await number_of_reports_generated_race_condition_resolved()
        await number_of_reports_generated_race_condition_resolved()
        await number_of_reports_generated_race_condition_resolved()
        await generate_report()

        end = time.perf_counter()

        print(f"\nTime taken by sequential_execution: {end - start:.2f} seconds\n")
    except Exception as e:
        print(f"Caught exception: {e}")


# =============================================
# ENTRY POINT
# =============================================
# Runs both modes back-to-back to compare timing and behavior.
async def main():
    await concurrent_execution()
    await sequential_execution()


# print(asyncio.run(main()))
