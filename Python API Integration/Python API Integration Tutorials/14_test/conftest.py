import pytest

# conftest.py is a special pytest file.
# Any fixture defined here is automatically available to every test file in the same
# directory and its subdirectories — no explicit import needed. pytest discovers it on its own.


@pytest.fixture
def managed_resource():
    # Simulates acquiring an exclusive resource (e.g. a lock, a DB connection, a file handle).
    # Everything BEFORE `yield` is SETUP — runs before the test function executes.
    # Everything AFTER `yield` is TEARDOWN — runs after the test, even if the test fails.
    print("[SHARED FIXTURE]: acquiring resource lock")
    resource = {"status": "lock_acquired"}
    yield resource                            # the test receives this dict as its argument
    print("[SHARED FIXTURE]: releasing resource lock")
    resource["status"] = "lock_released"
