# Pytest library will by default identify

# funtions that start with test_ in the .py files, that start with test_ or ends with _test
# To run just write pytest in terminal or cmd
# To test in verbose, run pytest -v -> it will print the name of function, file and final state of test
# To print the test summary for current test, run pytest -ra
# To print the summary of all the test, run pytest -rA

# text_analysis.py is the module under test — it contains the real logic we are verifying.
from text_analysis import calculate_text_attributes
import pytest

# Section: Pytest and 'assert'
# pytest rewrites `assert` statements at collection time so that when they fail,
# pytest prints the actual vs expected values automatically — no need for assertEqual() etc.


def test_string_equality() -> None:
    # Basic equality check — verifies that .upper() produces the expected casing.
    expected_status = "SUCCESS"
    actual_status = "success".upper()

    assert expected_status == actual_status


def test_word_count() -> None:
    # Tests both a normal sentence and an edge case (empty string).
    # Always test edge cases alongside happy paths.
    text = "Deploying microservices to Kubernetes cluster"
    text_empty = ""

    assert (calculate_text_attributes(text)["word_count"]) == 5
    assert (calculate_text_attributes(text_empty)["word_count"]) == 0


def test_unique_words() -> None:
    # "hello" appears twice — unique count should be 2, not 3.
    text = "hello honey hello"
    text_empty = ""

    assert (calculate_text_attributes(text)["unique_words"]) == 2
    assert (calculate_text_attributes(text_empty)["unique_words"]) == 0


def test_avg_word_length() -> None:
    # hello=5, hi=2, honourable=10, man=3 → total=20, avg=20/4=5.0
    text = "hello hi honourable man"
    text_empty = ""

    assert (calculate_text_attributes(text))["average_word_length"] == 5.0
    assert (calculate_text_attributes(text_empty))["average_word_length"] == 0.0


def test_longest_word() -> None:
    text = "hello hi honourable man"
    text_empty = ""

    assert (calculate_text_attributes(text))["longest_word"] == "honourable"
    assert (calculate_text_attributes(text_empty))["longest_word"] == ""


# pytest.approx for floating tolerance
def test_float_with_approx() -> None:
    calc_value = 0.1 + 0.2
    expected_value = 0.3

    # `0.1 + 0.2` is NOT exactly 0.3 in IEEE 754 floating-point arithmetic —
    # it evaluates to 0.30000000000000004. Direct `==` would fail.
    # pytest.approx() wraps the expected value with a small tolerance (1e-6 by default)
    # so the assertion passes for values that are "close enough".
    # gives error
    # assert calc_value == expected_value

    assert calc_value == pytest.approx(expected_value)



