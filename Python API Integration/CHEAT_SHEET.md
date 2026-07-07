# Python API Integration — Cheat Sheet
> Quick recall reference for everything covered in `Python API Integration Tutorials/`

---

## 1. Requests — CRUD & Centralized Handler (`01`)

```python
import requests

# Centralized handler — all CRUD goes through here
def make_request(method, url, **kwargs):
    try:
        response = requests.request(method, url, timeout=10, **kwargs)
        response.raise_for_status()   # raises HTTPError for 4xx/5xx
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

# response.json()   → JSON string → Python dict/list
# json.dumps(obj)   → Python dict/list → JSON string (for printing/saving)
```

---

## 2. Authentication (`02_01`)

```python
# Method 1: API Key as query param
params = {"q": "Delhi", "appid": API_KEY}
response = requests.get(url, params=params)    # auto-converts to ?q=Delhi&appid=...

# Method 2: Bearer Token in headers
headers = {"Authorization": f"Bearer {TOKEN}"}
response = requests.get(url, headers=headers)
```

---

## 3. OAuth 2.0 — Google (`02_02`)

```python
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

creds = None
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())           # silent refresh using refresh_token
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)   # opens browser first time only
    with open('token.json', 'w') as token:
        token.write(creds.to_json())       # persist so next run skips browser
```

**Flow:**
- First run → browser opens → saves `token.json`
- Next runs → uses saved token, no browser
- Token expires (~1hr) → auto-refreshed via `refresh_token`
- Re-auth only if: token deleted, scopes changed, token revoked

---

## 4. Secrets / `.env` (`05`)

```python
from dotenv import load_dotenv
import os

load_dotenv()   # loads .env into os.environ

TOKEN = os.getenv("GITHUB_TOKEN")
if not TOKEN:
    raise ValueError("Missing credentials — check .env")   # always validate!
```

**Critical:**  
- Add `.env` to `.gitignore` — never commit secrets
- Load at the **top** of the script before any `os.getenv()` calls
- Use `Path(__file__).resolve().parent / ".env"` for path-safe loading

---

## 5. Exception Handling (`03`)

```python
# Catch specific, not broad
try:
    event_id = entry['event_id']   # KeyError if missing
    user = entry.get('user', 'system')   # .get() for optional keys
except KeyError:
    ...
except (TypeError, AttributeError):   # None or non-dict entries
    ...

# Raise exceptions over returning None — forces caller to handle explicitly
def process(server_list):
    if not isinstance(server_list, list):
        raise TypeError("Must be a list")
    if len(server_list) == 0:
        return   # valid edge case — just return

# TypeError = wrong type  |  ValueError = right type, bad value
```

---

## 6. Logging (`04_01`, `04_02`)

```python
import logging, sys

logger = logging.getLogger("app.network")   # hierarchy: root → app → app.network
logger.setLevel(logging.DEBUG)   # logger gate — messages below this are dropped

stream_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler("app.log", "a")   # "a" = append

stream_handler.setLevel(logging.WARNING)   # handler gate — independent per handler
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)
```

**Key rules:**
- Logger level AND handler level BOTH must pass for a message to appear
- Child loggers propagate to parent by default
- JSON logging: use a custom `Formatter` that returns `json.dumps(record.__dict__)`

---

## 7. Retry with Exponential Backoff (`07`)

```python
MAX_RETRIES = 3

def get_info(url, **kwargs):
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, timeout=10, **kwargs)

            if response.status_code in (429, 500, 502, 503):
                wait = 2 ** attempt   # 1s → 2s → 4s
                time.sleep(wait)
                continue   # retry

            response.raise_for_status()   # other 4xx/5xx — raise immediately
            return response.json()

        except requests.exceptions.RequestException as e:
            return None   # non-retryable network error — bail

    return None   # all retries exhausted
```

**Why 403 is excluded:** retrying a forbidden request won't help — you need a new key.

---

## 8. Generators (`09`)

```python
# yield pauses execution and freezes local state
def count(val):
    i = 0
    while i <= val:
        i += 1
        yield i   # pauses here, resumes on next next() call

gen = count(3)
# next(gen) → resumes from last yield

# gen vs g() inside next():
# next(gen)   → same object, state preserved between calls
# next(g())   → new generator every time, always restarts from top

# yield from — delegates to another iterable
def chain(a, b):
    yield from a
    yield from b
```

**Generator exhaustion:** once `StopIteration` is raised, the generator is done — create a new one.

---

## 9. Functions as First-Class Citizens (`10`)

```python
# Assign to variable
say_hello = greet

# Pass as argument
def apply(operation, *operands):
    return operation(*operands)

# Return from function (factory pattern)
def create_api_client(auth_token):
    def api_client(endpoint, method):
        return f"Calling {endpoint} with {auth_token}"
    return api_client   # returns the inner function, not its result

# Store in data structures
pipeline = [validate, transform, send]
for step in pipeline:
    step()
```

---

## 10. Decorators (`11`)

```python
from functools import wraps

# Basic decorator
def check_runtime(func):
    @wraps(func)   # preserves __name__, __doc__ — always use this
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"Time: {time.time() - start:.5f}s")
        return result
    return wrapper

@check_runtime   # sugar for: my_func = check_runtime(my_func)
def my_func(): ...

# Decorator WITH arguments (3 levels)
def retry(max_attempts=3):      # level 1: config
    def decorator(func):        # level 2: receives the function
        @wraps(func)
        def wrapper(*args, **kwargs):   # level 3: runs on every call
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise   # re-raise — don't swallow the error
        return wrapper
    return decorator

@retry(4)
def flaky(): ...
```

---

## 11. Static Typing (`12`)

```python
from typing import Optional, Any, TypedDict, NotRequired

# Variable annotations
config_path: str = "/etc/app.conf"
identifier: str | int = "abc-123"
servers: list[str] = ["web1", "web2"]
settings: dict[str, int | str] = {"port": 8080}

# Function annotations
def get_status(hostname: str, port: int) -> str: ...
def log(msg: str) -> None: ...

# TypedDict — specific keys with specific types (stricter than dict[str, ...])
class User(TypedDict):
    id: int
    name: str
    phone: NotRequired[str]   # optional key

# Run mypy: python -m mypy my_file.py
# Add to CI/CD for enforcement
```

---

## 12. Context Managers (`13`)

```python
# Built-in — 'with' guarantees cleanup even if an exception occurs
with open("file.txt", "w") as f:
    f.write("data")   # file auto-closed after block, even on error

# Class-based custom context manager
class MyContextManager:
    def __enter__(self):
        # setup — return value goes to 'as' variable
        return "resource"

    def __exit__(self, exc_type, exc_val, exc_tb):
        # teardown — always runs
        return False   # False = re-raise exceptions | True = suppress them

# contextlib approach (simpler)
from contextlib import contextmanager

@contextmanager
def change_dir(destination):
    original = os.getcwd()
    try:
        os.chdir(destination)
        yield os.getcwd()   # value goes to 'as' variable
    finally:
        os.chdir(original)  # always reverts, even on error
```

---

## 13. Async (`15`)

### Core Concepts
```python
import asyncio

# async def creates a coroutine — doesn't run until awaited
async def fetch(url): ...

# gather — run multiple coroutines CONCURRENTLY (not parallel)
results = await asyncio.gather(fetch(url1), fetch(url2), fetch(url3))

# as_completed — process results as they finish (not in order)
import asyncio
tasks = [asyncio.create_task(fetch(url)) for url in urls]
for coro in asyncio.as_completed(tasks):
    result = await coro
```

### Blocking code in async
```python
# WRONG — freezes the entire event loop
async def bad():
    time.sleep(5)   # blocks everything

# CORRECT — offload to thread, event loop stays free
async def good():
    await asyncio.to_thread(time.sleep, 5)

# CPU-bound work — use ProcessPoolExecutor (threads won't help, GIL)
from concurrent.futures import ProcessPoolExecutor
async def cpu_work():
    loop = asyncio.get_event_loop()
    with ProcessPoolExecutor() as pool:
        await loop.run_in_executor(pool, cpu_heavy_func, arg)
```

### Semaphore — limit concurrent requests
```python
semaphore = asyncio.Semaphore(10)   # max 10 concurrent at a time

async def limited_fetch(url):
    async with semaphore:
        return await client.get(url)
```

### Circuit Breaker — shared protection pattern
```
States: CLOSED → OPEN → HALF-OPEN → CLOSED

CLOSED:    Normal. Requests go through. Failures counted.
OPEN:      Failure threshold hit. All requests fast-fail. Cooldown timer starts.
HALF-OPEN: Cooldown expired. One probe request sent.
            Probe succeeds → CLOSED | Probe fails → OPEN again
```

**vs Retry:** Retry is per-user/independent. Circuit Breaker is shared — after N failures, ALL users are protected, not just one.

### Token Bucket — rate limiting
```python
# Allows bursts up to bucket capacity, refills at a steady rate
# tokens -= 1 per request | tokens += rate per second (up to capacity)
# If tokens < 1 → wait until refilled
```

---

## Key Patterns to Remember

| Pattern | When to use |
|---|---|
| `make_request()` wrapper | Centralize error handling for all CRUD |
| `raise_for_status()` | Auto-raise on any 4xx/5xx |
| `response.json()` | Parse response to Python object |
| `json.dumps(obj, indent=2)` | Pretty-print Python object as JSON |
| `@wraps(func)` | Always use inside decorators |
| `__exit__ return False` | Re-raise exceptions (default) |
| `__exit__ return True` | Suppress exceptions |
| `yield` vs `return` | yield = lazy/pausable, return = eager/done |
| `asyncio.to_thread()` | Move sync blocking calls off event loop |
| `Semaphore` | Limit concurrency (I/O bound) |
| `ProcessPoolExecutor` | True parallelism (CPU bound) |
| Circuit Breaker | Shared resource protection across all users |
