from yival.cli.utils import generate_experiment_config_yaml
from yival.schemas.experiment_config import WrapperConfig, WrapperVariation


# Mocking the required classes and methods
class MockedDefaultConfig:

    def __init__(self, **kwargs):
        self.__dict__ = kwargs


def test_generate_experiment_config_yaml():
    # Calling the function without any special arguments
    result = generate_experiment_config_yaml(custom_function="module.function")

    # Assertions for default values
    assert "description: Generated experiment config" in result
    assert "source_type: dataset" in result

    # Calling the function with specific arguments
    result_with_args = generate_experiment_config_yaml(
        custom_function="module.function",
        source_type="USER",
        evaluator_names=["string_expected_result"],
        wrapper_names=["string_wrapper"],
        wrapper_configs=[
            WrapperConfig(
                name="sample_wrapper",
                variations=[
                    WrapperVariation(
                        value_type="str", value="example_variation"
                    )
                ]
            )
        ]
    )
    # Assertions for provided arguments
    assert "source_type: USER" in result_with_args
    assert "string_expected_result" in result_with_args
    assert "string_wrapper" in result_with_args
    assert "example_variation" in result_with_args
