import pytest

# Defining a simple fixture
ConfigDict = dict[str, int | str]


@pytest.fixture
def sample_config_dict() -> ConfigDict:
    return {"api_url": "https://test.api.example.com", "timeout": 30, "retries": 3}


def test_api_url(sample_config_dict: ConfigDict):
    print("[TEST]: test_api_url is running...")
    assert "api_url" in sample_config_dict
    assert sample_config_dict["api_url"] == "https://test.api.example.com"


# provide an example of fixture which consists of setup code, yield and teardown code


# Scope or Lifecycle function and session
# Function scope
@pytest.fixture(scope="function")
def servers_info_func():
    print("\n[Function Scope SETUP CODE] Run before the test")
    yield {"server": "Ubuntu", "hostname": "EC2"}
    print("[Function Scope TEARDOWN CODE] Run after the test")


def test_server_details_func(servers_info_func):
    print("[TEST]: server test is running...")
    assert servers_info_func.get("server") == "Ubuntu"


def test_hostname_details_func(servers_info_func):
    print("[TEST]: hostname test is running...")
    assert servers_info_func.get("hostname") == "EC2"


# Session scope
@pytest.fixture(scope="session")
def servers_info_session():
    print("\n[Session Scope SETUP CODE] Run before the test")
    yield {"server": "Ubuntu", "hostname": "EC2"}
    print("[Session Scope TEARDOWN CODE] Run after the test")


def test_server_details_session(servers_info_session):
    print("[TEST]: server test is running...")
    assert servers_info_session.get("server") == "Ubuntu"


def test_hostname_details_session(servers_info_session):
    print("[TEST]: hostname test is running...")
    assert servers_info_session.get("hostname") == "EC2"


# Global Scope -> Run Setup Code before and Teardown code after all the test
@pytest.fixture(scope="session", autouse=True)
def global_setup():
    print("\n[Global Scope SETUP CODE] Run before all the test")
    yield None
    print("[Global Scope TEARDOWN CODE] Run after all the test")


# Sharing Fixtures with conftest.py
def test_managed_reosurces(managed_resource):
    assert managed_resource["status"] == "lock_acquired"


# NOTE - you can see that , even if the session fixture is not called here, it still executing the teardown code after this func runs completely...so it will run till the session ends.
