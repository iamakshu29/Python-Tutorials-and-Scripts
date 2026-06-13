import asyncio
import time

count = 0


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
    await fetch_users()  # because of strtech goal requirement 1 - dependency
    print("Generating Users Report using Excel")
    await asyncio.sleep(4)
    print("Report Generated Successfully")
    raise ValueError(
        "Something went wrong"
    )  # because of stretch goal requirement 2 - show failed job


# because of stretch goal requirement 3 - show race conditions
async def number_of_reports_generated_race_condition():
    global count
    temp = count  # READ — all three read before anyone writes
    await asyncio.sleep(1)  # YIELD — gap between read and write
    count = temp + 1  # WRITE — all three write 0+1=1
    print(f"reports generated when race condition exists {count}")


async def number_of_reports_generated_race_condition_resolved():
    global count
    await asyncio.sleep(1)  # YIELD — gap before read
    temp = count  # READ — all three read before anyone writes
    count = temp + 1  # WRITE — all three write 0+1=1
    print(f"reports generated after race conditions resolved {count}")


### As you can see we resolved the race condition by placing the await before yielding...so its just special case or creating answer like that
# You're not resolving the race condition by moving the await.
# You're just accidentally avoiding it because of how your specific code is structured.
# A different sleep duration, a different number of coroutines, or a more complex operation would break that assumption.

#### will learn in Module 2 -->
# We need to use asyncio.lock(), lock prevents any other coroutine from entering the block until the current one exits.


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
            return_exceptions=True,
        )

        end = time.perf_counter()

        print(f"\nTime taken by concurrent_execution: {end - start:.2f} seconds\n")
        return result
    except Exception as e:
        print(f"Caught exception: {e}")


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


async def main():
    await concurrent_execution()
    await sequential_execution()


# print(asyncio.run(main()))
