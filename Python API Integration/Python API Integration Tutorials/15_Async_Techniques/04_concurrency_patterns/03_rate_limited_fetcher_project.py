import asyncio
import time
import httpx
import random

# ================================================================================
# Rate-Limited Concurrent Fetcher
# ================================================================================
# Fetches 30 URLs concurrently with all patterns combined:
#   Semaphore(5)    → max 5 active requests at the same time
#   Counter+sleep   → pause after every 10 results (simple rate limit)
#   Retry           → 1 retry after 1s on any failure
#   Stats           → total, successful, failed, avg response time
#   Progress        → live "Completed: N/30" counter
# ================================================================================

async def fetch_url(client, URL, semaphore):
    # Retry loop: attempt the request up to 2 times before giving up.
    for _ in range(2):
        try:
            # Blocks here if 5 requests are already in flight.
            # Only 5 reach client.get() simultaneously — the rest wait at this line.
            async with semaphore:
                start_time = time.time()
                response = await client.get(URL)
                end_time = time.time()
                response.raise_for_status()
                return {
                    "url": URL,
                    "status": response.status_code,
                    "duration" : float(f"{end_time - start_time:.2f}")
                }
        except (httpx.HTTPStatusError, httpx.RequestError, Exception) as e:
            # Any failure: print, sleep 1s, then loop continues to attempt 2.
            # No return here — that's what allows the retry.
            print(f"Attempt failed: {e} — Retrying...")
            await asyncio.sleep(1)
    # Both attempts failed — always returns a dict (never None) so stats code is safe.
    return {"url": URL, "status": None, "duration": 0, "failed": True}



async def main():
    Delay_URL,Get_URL = "https://httpbin.io/delay", "https://httpbin.io/ge"
    progress_counter, total_duration, count, rate_limit, total_request = 0, 0, 0, 10, 30
    delays, coros = [0,1,2],[]
    semaphore = asyncio.Semaphore(5)

    track = {
        "Total Request" : 0,
        "Requests Failed": 0,
        "Requests Successful": 0,
        "Avg Response Time": ""
    }

    
    async with httpx.AsyncClient() as client:
        # Build exactly 30 coroutines — one per iteration, one URL per coroutine.
        for _ in range(total_request):
            URL = random.choice([Delay_URL, Get_URL])

            if URL == Delay_URL:
                # Pick ONE random delay per slot — no inner loop, no duplicates.
                delay = random.choice(delays)
                res = fetch_url(client, f"https://httpbin.io/delay/{delay}", semaphore)
            else:
                res = fetch_url(client, URL, semaphore)

            coros.append(res)

        # as_completed: all 30 coroutines start immediately, results arrive fastest-first.
        for future in asyncio.as_completed(coros):
            if count >= rate_limit:
                # After every 10 results, pause 4s before continuing — simple rate gate.
                print("\n======================")
                print("Rate Limit Engaging:")
                print("======================\n")
                await asyncio.sleep(4)
                count = 0
            result = await future
            print(f"Got result: {result!r}")
            count += 1

            # duration is always a float (0 for failures) — safe to add regardless.
            total_duration += result["duration"]
            track["Total Request"] += 1
            progress_counter += 1
            print(f"Completed: {progress_counter}/{total_request}")

            if result.get("failed"):
                track["Requests Failed"] += 1
            else:
                track["Requests Successful"] += 1

        # Avg calculated once after all results — guard against all-failed case.
        if track["Requests Successful"] > 0:
            track["Avg Response Time"] = round(total_duration / track["Requests Successful"], 3)
        print()
        return track
            
print(asyncio.run(main()))