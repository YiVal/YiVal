import tempfile

import pytest

from ..configs.config_utils import load_and_validate_config
from ..schemas.experiment_config import (
    ExperimentConfig,
    WrapperConfig,
    WrapperVariation,
)
from .utils import generate_experiment_config_yaml


@pytest.mark.parametrize(
    "evaluator_names,reader_name,wrapper_names,source_type,wrapper_configs",
    [
        (["string_expected_result"], None, None, "dataset", [
            WrapperConfig(
                name="sample_wrapper",
                variations=[
                    WrapperVariation(
                        value_type="str", value="example_variation"
                    )
                ]
            )
        ]),
        # ... other parameter combinations for more thorough testing ...
    ]
)
def test_generate_and_load_config(
    evaluator_names, reader_name, wrapper_names, source_type, wrapper_configs
):
    # Generate a sample config using our utility function
    yaml_config = generate_experiment_config_yaml(
        custom_function="module.function",
        evaluator_names=evaluator_names,
        reader_name=reader_name,
        wrapper_names=wrapper_names,
        source_type=source_type,
        wrapper_configs=wrapper_configs
    )

    # Create a temporary file to store our config
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        temp_file.write(yaml_config)
        temp_file_path = temp_file.name

    f = open(temp_file_path, "r")
    print(f.read())

    # Load the config using OmegaConf
    loaded_config = load_and_validate_config(temp_file_path)
    print(loaded_config)
    loaded_config = ExperimentConfig(**loaded_config)

    # Basic assertions to check the loaded configuration
    assert loaded_config.description == "Generated experiment config"

    # If wrapper_configs were provided, we should have a "wrappers" section in our config
    if wrapper_configs:
        assert loaded_config.variations is not None
        for wrapper in loaded_config.variations:
            assert any(wc.name == wrapper["name"] for wc in wrapper_configs)

    # If evaluator_names were provided, we should have an "evaluators" section in our config
    if evaluator_names:
        assert loaded_config.evaluators is not None
        for evaluator in loaded_config.evaluators:
            assert evaluator["name"] in evaluator_names

    # Additional checks can be added here as necessary
