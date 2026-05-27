import time
from datetime import timedelta, timezone

start_time = time.time()
count = 0
expires_at = start_time + timedelta(seconds=5).total_seconds()


def rate_limiter(start_time, expires_at):
    global count
    start_time = time.time()
    count += 1
    print(count)
    # print(f"Expiry at {expires_at} and start at {start_time}")
    if count > 5:
        return f"API Hit Limit Reaches, wait for {expires_at - start_time}"


# for i in range(6):
#     print(rate_limiter(start_time, expires_at))
