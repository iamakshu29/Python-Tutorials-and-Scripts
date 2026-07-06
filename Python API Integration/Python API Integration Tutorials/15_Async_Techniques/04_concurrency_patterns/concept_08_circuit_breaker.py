import asyncio

# ================================================================================
# CONCEPT 8 — Circuit Breaker Pattern
# ================================================================================
#
# Problem: if a service is down, you keep hammering it with requests (and failing fast)
# Circuit breaker: after N failures, "open" the circuit — stop trying for a cooldown period
# States: CLOSED (normal) → OPEN (failing, don't try) → HALF-OPEN (test one request)
#
# ================================================================================
# NOTES — Understanding the idea behind it
# ================================================================================
#
# Q1. Why Circuit Breaker instead of exponential backoff retry for a service?
#
#     Exponential backoff is PER USER, INDEPENDENT. Each user has no idea what others are doing:
#       User 1:    hit → fail → wait 1s → hit → fail → wait 2s → hit → fail → wait 4s...
#       User 2:    hit → fail → wait 1s → hit → fail → wait 2s → ... (independently)
#       User 1000: same...
#     So 1000 users × 3 retries each = 3000 hits on an already-dying service before anyone backs off. No coordination.
#
#     Circuit Breaker is SHARED, GLOBAL. One object, one state, all users go through it:
#       User 1 → fail (count=1)
#       User 2 → fail (count=2)
#       User 3 → fail (count=3) → TRIPS → Circuit OPEN
#       User 4 to 1000 → fast-fail instantly, service never touched
#     Just 3 hits before protection kicks in. It's a shared gate, not per-user logic.
#     It's not about one user retrying — it's about protecting a shared resource from a flood.
#
# ─────────────────────────────────────────────────────────────────────────────────
#
# Q2. State changes — are they for the NEXT request, not the current one?
#
#     Yes, exactly. The current call is already past the check at the top.
#     State changes in try-except block, always take effect for the NEXT call.
#
#     And timing works the same way:
#       Request #3 → except block → opened_at = current_time    ← recorded here
#       Request #4 → top of call() → elapsed = current_time - opened_at  ← read here
#
#     opened_at is written once (when circuit trips), read on every subsequent
#     request until the circuit resets. The gap between those two moments IS
#     the elapsed time.
#
# Q2.1. What is this asyncio.get_event_loop().time() ?
#
#     asyncio.get_event_loop().time() is like time.perf_counter() — both return
#     a float in seconds (monotonic, never goes backwards). The asyncio version
#     uses the same internal clock the event loop uses for scheduling.
#     You subtract start from end to get elapsed seconds. That's it.
#
# ─────────────────────────────────────────────────────────────────────────────────
#
# Q3. What is HALF_OPEN? Either we can hit a request or we can't — what's in between?
#
#     While the circuit is OPEN, how do you know when the service recovers?
#     You can't know without trying. But you can't send all 1000 users through
#     to test — if the service is still fragile, that floods it again and re-trips.
#
#     HALF_OPEN = send exactly ONE test request ("probe"):
#       - Succeeds → CLOSED (recovered, let everyone through)
#       - Fails    → OPEN again (still down, start cooldown over)
#
#     It's a controlled single knock on the door before opening it fully.
#
# ================================================================================


async def external_service():
    await asyncio.sleep(0.1)                  # simulate network delay
    raise ConnectionError("Service down")     # simulate failure
    # To test recovery: comment the raise above after the cooldown sleep in main()

async def external_service_2():
    # Healthy service — succeeds immediately. Simulates recovery after cooldown.
    await asyncio.sleep(0.1)


class CircuitBreaker:
    def __init__(self, failure_threshold, cooldown):
        self.state             = "CLOSED"     # always starts CLOSED
        self.failure_count     = 0
        self.failure_threshold = failure_threshold
        self.cooldown          = cooldown
        self.opened_at         = None         # timestamp when it tripped to OPEN

    async def call(self, func):
        # If OPEN: check if cooldown has passed → maybe move to HALF_OPEN → to send exactly one test requst to check
        if self.state == "OPEN":
            elapsed = asyncio.get_event_loop().time() - self.opened_at
            if elapsed >= self.cooldown:
                self.state = "HALF_OPEN"
                print(f"  [CB] Cooldown elapsed → HALF_OPEN, sending probe...")
            else:
                print(f"  [CB] Circuit OPEN — fast-fail (cooldown: {elapsed:.1f}s / {self.cooldown}s elapsed)")
                return

        # CLOSED / HALF_OPEN: attempt the actual call
        try:
            await func()
            # Success — reset everything. Even a HALF_OPEN probe success closes the circuit.
            print(f"  [CB] Service OK → state=CLOSED, failure_count reset")
            self.failure_count = 0
            self.state = "CLOSED"
        except Exception as e:
            self.failure_count += 1
            if self.state == "HALF_OPEN" or self.failure_count >= self.failure_threshold:
                reason = "Probe failed" if self.state == "HALF_OPEN" else f"Threshold hit ({self.failure_count}/{self.failure_threshold})"
                self.state = "OPEN"
                self.opened_at = asyncio.get_event_loop().time()  # timestamp used to measure cooldown elapsed time
                print(f"  [CB] {reason} → state=OPEN, cooldown starts ({self.cooldown}s)")
            else:
                print(f"  [CB] Failure {self.failure_count}/{self.failure_threshold} — state=CLOSED | {e}")


# main() = the "user" — owns the loop, hits the circuit breaker N times
async def main():
    cb = CircuitBreaker(failure_threshold=3, cooldown=2.0)

    for i in range(5):
        print(f"\n[User] Request #{i+1}")
        await cb.call(external_service)

    print("\n--- waiting 2.1s for cooldown ---")
    await asyncio.sleep(2.1)              # let cooldown expire → next request probes (HALF_OPEN)

    for i in range(5, 10):
        print(f"\n[User] Request #{i+1}")
        # await cb.call(external_service) # Service always unhealthy
        await cb.call(external_service_2) # Service get healthy service after cooldown

asyncio.run(main())
