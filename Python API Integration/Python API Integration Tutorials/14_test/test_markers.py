# Section Markers
# Markers are labels you attach to test functions to control how pytest runs them.
# Built-in markers: skip, skipif, xfail, parametrize.
# Custom markers can also be defined (registered in pyproject.toml to avoid warnings).
import pytest
import time


# SubSection Skipping test unconditionally @pytest.mark.skip
# reason is optional in both skip and skipif
# Use when a test is intentionally disabled (WIP, broken env, etc.)
@pytest.mark.skip(reason="Experimenting....")
def test_new_experimental_feature_2() -> None:
    assert False


try:
    import someModule
except ModuleNotFoundError:
    someModule = None


# SubSection Skipping test conditionally @pytest.mark.skipif
# The condition is evaluated at collection time (before the test runs).
# If the condition is True, the test is skipped entirely — not counted as a failure.
@pytest.mark.skipif(
    someModule is None, reason="Requires, 'some_optional_module' to be installed"
)
def test_with_optional_dependency() -> None:
    assert someModule


# SubSection Expected Failures: @pytest.mark.xfail
# Marking tests as expected failure -> This will provide the exit code 0 as its expected failure
# and pipeline will not fail and continue to run for other tests.
# Result codes:
#   XFAIL  → test failed as expected          (✓ pipeline continues)
#   XPASS  → test PASSED despite being marked xfail (pytest reports this as a warning by default)
@pytest.mark.xfail(reason="A Known Bug")
def test_div_by_zero() -> None:
    _division = 1 / 0
    assert False


# This test is marked xfail but will actually PASS → pytest reports it as XPASS.
# XPASS means the bug may have been fixed — worth investigating and removing the xfail marker.
@pytest.mark.xfail
def test_expected_to_fail() -> None:
    assert True


# SubSection Custom Markers and Registration
# Custom markers must be registered in pyproject.toml (under [tool.pytest.ini_options] → markers)
# otherwise pytest raises a PytestUnknownMarkWarning.
# Run a specific marker: pytest -m <marker_name>
# Combine:  pytest -m "api and smoke"   /  pytest -m "slow or api"  /  pytest -m "not slow"
@pytest.mark.slow
def test_very_long_computatuons() -> None:
    time.sleep(5)
    assert True


@pytest.mark.api
@pytest.mark.smoke
def test_user_creation() -> None:
    assert True