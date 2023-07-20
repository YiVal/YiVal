from .experiment_state import ExperimentState


class CustomType:
    def __init__(self, value):
        self.value = value


def test_default_state():
    state = ExperimentState()
    assert not state.active
    assert state.current_variations == {}
    assert state.counters == {}


def test_get_next_variation_without_setting():
    state = ExperimentState()
    assert state.get_next_variation("test_experiment") is None


def test_get_next_variation_with_string_variations():
    state = ExperimentState()
    state.set_variations_for_experiment("test_experiment", ["var1", "var2"])
    assert state.get_next_variation("test_experiment") == "var1"
    assert state.get_next_variation("test_experiment") == "var2"
    assert state.get_next_variation("test_experiment") is None  # No more variations


def test_get_next_variation_with_mixed_variations():
    state = ExperimentState()
    custom_obj = CustomType("custom_value")
    state.set_variations_for_experiment(
        "mixed_test_experiment", ["var1", 42, custom_obj]
    )
    assert state.get_next_variation("mixed_test_experiment") == "var1"
    assert state.get_next_variation("mixed_test_experiment") == 42
    assert state.get_next_variation("mixed_test_experiment") == custom_obj
    assert (
        state.get_next_variation("mixed_test_experiment") is None
    )  # No more variations
