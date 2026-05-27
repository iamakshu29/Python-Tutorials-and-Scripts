import pytest


def test_equal_or_not_equal():
    assert 3 == 3
    assert 3 != 1


# Validating Instances
def test_validate_instance():
    assert isinstance("This is a string", str)
    assert not isinstance("10", int)


# Validating Booleans
def test_boolean():
    validated = True
    assert validated is True
    assert ("hello" == "world") is False


# Validating Types
def test_type():
    assert type("Hello" is str)
    assert type("Hello" is not int)


# Python Basics Validation
def test_greater_and_less_than():
    assert 7 > 3
    assert 4 < 10


# Validation Num Types
def test_list():
    num_list = [1, 2, 3, 4, 5]
    any_list = [False, False]

    assert 1 in num_list
    assert 7 not in num_list
    assert all(num_list)  # return true, if all values are truthy
    assert not any(any_list)  # return true, if atleast one value is truthy


# Pytest Object
# Creating our own Python Object


class Student:
    def __init__(self, first_name: str, last_name: str, major: str, years: int):
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.years = years


def test_person_initialization():
    p = Student("John", "Snow", "CSE", 3)
    assert p.first_name == "John", "First name should be John"  # Message is Optional
    assert p.last_name == "Snow", "Last name should be Snow"
    assert p.major == "CSE"
    assert p.years == 3


# now using pytest.fixture, we don't have to create a new object everytime to test it, we can simply pass the func_name as paramter and use to to test the attributes with dot operator
@pytest.fixture
def default_employee():
    return Student("John", "Snow", "CSE", 3)


def test_person_initialization_using_fixture(default_employee):
    assert default_employee.first_name == "John", "First name should be John"
    assert default_employee.last_name == "Snow", "Last name should be Snow"
    assert default_employee.major == "CSE"
    assert default_employee.years == 3
