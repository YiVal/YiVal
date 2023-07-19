from ..states.experiment_state import ExperimentState
from .string_wrapper import StringWrapper


def setup_function():
    # Resetting the _instance attribute to None before each test
    # to ensure a clean slate for each test (important for testing singletons)
    ExperimentState._instance = None


def test_string_representation_without_variation():
    instance = StringWrapper(original_string="Hello", name="greeting")
    assert str(instance) == "Hello"


def test_string_representation_with_variation():
    # Setting up the ExperimentState with an active state and a variation for the
    # 'greeting' experiment
    state = ExperimentState()
    state.active = True
    state.current_variations["greeting"] = ["Hi"]

    instance = StringWrapper(original_string="Hello", name="greeting")
    assert str(instance) == "Hi"


def test_string_representation_with_inactive_experiment_state():
    # Setting up the ExperimentState with an inactive state
    state = ExperimentState()
    state.active = False
    state.current_variations["greeting"] = ["Hi"]

    instance = StringWrapper(original_string="Hello", name="greeting")
    assert str(instance) == "Hello"


def test_string_representation_with_no_variation():
    # Setting up the ExperimentState with an active state but no variation for the
    # 'greeting' experiment
    state = ExperimentState()
    state.active = True

    instance = StringWrapper(original_string="Hello", name="greeting")
    assert str(instance) == "Hello"
