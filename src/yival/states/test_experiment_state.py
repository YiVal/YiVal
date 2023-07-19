import pytest

from .experiment_state import ExperimentState


def setup_function():
    # Resetting the _instance attribute to None before each test
    # to ensure clean slate for each test (important for testing singletons)
    ExperimentState._instance = None


def test_singleton_behavior():
    # Creating two instances
    instance1 = ExperimentState()
    instance2 = ExperimentState()

    # Asserting that both instances are the same
    assert instance1 is instance2


def test_default_attributes():
    instance = ExperimentState()

    # Checking default attributes
    assert not instance.active
    assert instance.current_variations == {}
    assert instance.counters == {}
    assert instance.initialized


def test_get_next_variation_without_variations():
    instance = ExperimentState()
    result = instance.get_next_variation("test")
    assert result is None


def test_get_next_variation_with_variations():
    instance = ExperimentState()
    instance.current_variations["test"] = ["variation1", "variation2"]

    # Check that the variations are rotated through correctly
    assert instance.get_next_variation("test") == "variation1"
    assert instance.get_next_variation("test") == "variation2"
    assert instance.get_next_variation(
        "test"
    ) == "variation1"  # should wrap around


def test_thread_safety():
    import threading

    instance = ExperimentState()
    instance.current_variations["test"] = ["variation1", "variation2"]

    # Function to be run in a thread
    def thread_func():
        for _ in range(1000):  # Call get_next_variation many times
            instance.get_next_variation("test")

    # Start multiple threads
    threads = [threading.Thread(target=thread_func) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # After all threads finish, the counter should be 10,000 (10 threads * 1000
    # iterations)
    assert instance.counters["test"] == 10000
