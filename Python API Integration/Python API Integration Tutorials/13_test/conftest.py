import pytest


@pytest.fixture
def managed_resource():
    print("[SHARED FIXTURE]: acquiring resource lock")
    resource = {"status": "lock_acquired"}
    yield resource
    print("[SHARED FIXTURE]: releasing resource lock")
    resource["status"] = "lock_released"
