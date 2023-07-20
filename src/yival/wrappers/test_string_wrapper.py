from ..states.experiment_state import ExperimentState
from .string_wrapper import StringWrapper


def setup_function():
    # Resetting the _instance attribute to None before each test
    # to ensure a clean slate for each test (important for testing singletons)
    ExperimentState._instance = None


def test_string_representation_without_variation():
    # Initialize ExperimentState but don't set it as active
    state = ExperimentState.get_instance()
    state.active = False

    # Create a StringWrapper instance
    wrapper = StringWrapper("Hello", "test_experiment")
    assert str(wrapper) == "Hello"


def test_string_representation_with_variation():
    # Activate the ExperimentState and set a variation
    state = ExperimentState.get_instance()
    state.active = True
    state.set_variations_for_experiment("test_experiment", ["Hi"])

    # Create a StringWrapper instance
    wrapper = StringWrapper("Hello", "test_experiment")
    assert str(wrapper) == "Hi"


def test_string_representation_with_no_active_variation():
    # Set the ExperimentState to active but don't provide a variation
    state = ExperimentState.get_instance()
    state.active = True

    # Create a StringWrapper instance
    wrapper = StringWrapper("Hello", "test_experiment")
    assert str(wrapper) == "Hello"
