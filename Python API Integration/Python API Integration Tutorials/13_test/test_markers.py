# Section Markers
import pytest
import time


# SubSection Skipping test unconditionally @pytest.mark.skip
# reason is optional in both skip and skipif
@pytest.mark.skip(reason="Experimenting....")
def test_new_experimental_feature_2() -> None:
    assert False


try:
    import someModule
except ModuleNotFoundError:
    someModule = None


# SubSection Skipping test conditionally @pytest.mark.skipif
@pytest.mark.skipif(
    someModule is None, reason="Requires, 'some_optional_module' to be installed"
)
def test_with_optional_dependency() -> None:
    assert someModule


# SubSection Expected Failures: @pytest.mark.xfail
# Marking tests as expected failure -> This will provide the exit code 0 as its expected failute and pipeline will not fail and continue to run for other tests
@pytest.mark.xfail(reason="A Known Bug")
def test_div_by_zero() -> None:
    _division = 1 / 0
    assert False


@pytest.mark.xfail
def test_expected_to_fail() -> None:
    assert True


# SubSection Custom Markers and Registration
# run it using -m
# >> pytest -m <marker_name> with or, and, not
@pytest.mark.slow
def test_very_long_computatuons() -> None:
    time.sleep(5)
    assert True


@pytest.mark.api
@pytest.mark.smoke
def test_user_creation() -> None:
    assert True