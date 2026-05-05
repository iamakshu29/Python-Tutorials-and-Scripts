# Pytest library will by default identify 
    # funtions that start with test_ in the .py files, that start with test_ or ends with _test 
# To run just write pytest in terminal or cmd
# To test in verbose, run pytest -v -> it will print the name of function, file and final state of test
# To print the test summary for current test, run pytest -ra 
# To print the summary of all the test, run pytest -rA


# Section: Pytest and 'assert'
def test_string_equality() -> None:
    expected_status = "SUCCESS"
    actual_status = "success".upper()

    assert expected_status == actual_status

from text_analysis import calculate_text_attributes
def test_word_count() -> None:
    text = "Deploying microservices to Kubernetes cluster"
    text_empty = ""

    assert(calculate_text_attributes(text)["word_count"]) == 5
    assert(calculate_text_attributes(text_empty)["word_count"]) == 0

def test_unique_words() -> None:
    text = "hello honey hello"
    text_empty = ""

    assert(calculate_text_attributes(text)["unique_words"]) == 2
    assert(calculate_text_attributes(text_empty)["unique_words"]) == 0

def test_avg_word_length() -> None:
    text = "hello hi honourable man"
    text_empty = ""

    assert(calculate_text_attributes(text))["average_word_length"] == 5.0
    assert(calculate_text_attributes(text_empty))["average_word_length"] == 0.0

def test_longest_word() -> None:
    text = "hello hi honourable man"
    text_empty = ""

    assert(calculate_text_attributes(text))["longest_word"] == "honourable"
    assert(calculate_text_attributes(text_empty))["longest_word"] == ""