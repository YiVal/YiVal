import pytest

from yival.evaluators.utils import fuzzy_match_util


@pytest.mark.parametrize(
    "string1, string2, expected",
    [
        ("hello world!", "hello world", True),
        ("hello world", "hello", False),
        ("hello", "world", False),
        ("Hello", "hello", False),
        ("12345", "123", False),
        ("@!#@", "@", False),
    ],
)
def test_fuzzy_match_util_parametrized(string1, string2, expected):
    assert fuzzy_match_util(string1, string2) == expected
