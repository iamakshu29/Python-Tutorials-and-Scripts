import pytest

# A fixture is a function decorated with @pytest.fixture that provides a reusable piece of
# setup data or state to test functions. Instead of repeating setup logic in every test,
# you declare it once as a fixture and receive it as a parameter by name.

# Section: Fixtures

# --- Simple fixture (no teardown, no explicit scope) ---
# When no `scope` is set, pytest defaults to scope="function" — the fixture is called
# fresh for each test that requests it.
ConfigDict = dict[str, int | str]


@pytest.fixture
def sample_config_dict() -> ConfigDict:
    # Returns a plain dict — no resource to clean up, so no `yield` needed.
    return {"api_url": "https://test.api.example.com", "timeout": 30, "retries": 3}


def test_api_url(sample_config_dict: ConfigDict):
    print("[TEST]: test_api_url is running...")
    assert "api_url" in sample_config_dict
    assert sample_config_dict["api_url"] == "https://test.api.example.com"


# --- Fixture with Setup, yield, and Teardown ---
# Pattern:
#   1. Code before `yield`  → SETUP  (runs before the test)
#   2. `yield <value>`      → the test receives <value> as its argument
#   3. Code after  `yield`  → TEARDOWN (runs after the test, even if the test fails)
# Use this whenever you need to clean up a resource (close a connection, delete a file, etc.)

# SubSection Scope / Lifecycle
# scope controls HOW OFTEN a fixture is created and destroyed.

# --- scope="function" (default) ---
# A NEW instance is created before EACH test and torn down after EACH test.
# Use this when tests must be fully isolated and cannot share state.
@pytest.fixture(scope="function")
def servers_info_func():
    print("\n[Function Scope SETUP CODE] Run before the test")
    yield {"server": "Ubuntu", "hostname": "EC2"}
    print("[Function Scope TEARDOWN CODE] Run after the test")


def test_server_details_func(servers_info_func):
    print("[TEST]: server test is running...")
    assert servers_info_func.get("server") == "Ubuntu"


def test_hostname_details_func(servers_info_func):
    # servers_info_func is re-created here — a completely fresh dict, not the same object
    # that test_server_details_func received.
    print("[TEST]: hostname test is running...")
    assert servers_info_func.get("hostname") == "EC2"


# --- scope="session" ---
# Created ONCE for the entire test session (all test files combined) and torn down at the end.
# Use this for expensive setup that is safe to share across tests (e.g. a read-only DB connection,
# a pre-built client, or a large dataset that doesn't change).
@pytest.fixture(scope="session")
def servers_info_session():
    print("\n[Session Scope SETUP CODE] Run before the test")
    yield {"server": "Ubuntu", "hostname": "EC2"}
    print("[Session Scope TEARDOWN CODE] Run after the test")


def test_server_details_session(servers_info_session):
    print("[TEST]: server test is running...")
    assert servers_info_session.get("server") == "Ubuntu"


def test_hostname_details_session(servers_info_session):
    # servers_info_session is the SAME object that test_server_details_session received —
    # shared across all tests that request it within the session.
    print("[TEST]: hostname test is running...")
    assert servers_info_session.get("hostname") == "EC2"


# --- autouse=True ---
# When autouse=True, the fixture runs automatically for every test in scope WITHOUT the
# test needing to declare it as a parameter. Useful for global setup (e.g. resetting a
# DB state, configuring logging, or seeding environment variables) that every test needs.
@pytest.fixture(scope="session", autouse=True)
def global_setup():
    print("\n[Global Scope SETUP CODE] Run before all the test")
    yield None
    print("[Global Scope TEARDOWN CODE] Run after all the test")


# SubSection Sharing Fixtures via conftest.py
# `managed_resource` is defined in conftest.py, not in this file.
# pytest automatically discovers conftest.py and makes its fixtures available here —
# no import statement needed.
def test_managed_reosurces(managed_resource):
    assert managed_resource["status"] == "lock_acquired"


# NOTE - you can see that , even if the session fixture is not called here, it still executing the teardown code after this func runs completely...so it will run till the session ends.
