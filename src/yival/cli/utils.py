from enum import Enum
from typing import Any, Dict, List, Optional, Type

import yaml

from ..combination_improvers.base_combination_improver import (
    BaseCombinationImprover,
)
from ..data.base_reader import BaseReader
from ..data_generators.base_data_generator import BaseDataGenerator
from ..evaluators.base_evaluator import BaseEvaluator
from ..result_selectors.selection_strategy import SelectionStrategy
from ..schemas.experiment_config import WrapperConfig
from ..variation_generators.base_variation_generator import (
    BaseVariationGenerator,
)
from ..wrappers.base_wrapper import BaseWrapper


def recursive_asdict(obj) -> Any:
    if isinstance(obj, list):
        return [recursive_asdict(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: recursive_asdict(value) for key, value in obj.items()}
    elif isinstance(obj, Enum):  # Handle Enum values
        return obj.value
    elif hasattr(obj, 'asdict'):  # For dataclasses with asdict
        return obj.asdict()
    else:
        return obj


def get_default_config(component_class: Type[Any]) -> Optional[Dict[str, Any]]:
    """Retrieve the default configuration of a component, if available."""
    default = getattr(component_class, "default_config", None)
    if not isinstance(default, dict):
        return default.__dict__
    return default


def get_config_for_component(component_name, get_component_func):
    """Get configuration for a given component."""
    component_cls = get_component_func(component_name)
    if component_cls:
        default_config = get_default_config(component_cls)
        if default_config:
            return {component_name: default_config}
        else:
            return {component_name: {}}
    return {}


def generate_dataset_section(source_type, reader_name,
                             data_generator_names) -> Dict[str, Any]:
    """Generate the dataset section of the experiment config."""
    dataset_section = {"source_type": source_type}
    if source_type == "dataset":
        dataset_section["file_path"] = "/path/to/file_path"
    if reader_name and source_type == "dataset":
        dataset_section["reader"] = reader_name
        reader_config = get_config_for_component(
            reader_name, BaseReader.get_reader
        )
        if reader_config:
            dataset_section["reader_config"] = reader_config
    if data_generator_names and source_type == "machine_generated":
        data_generators_section = {}
        for name in data_generator_names:
            data_generator_config = get_config_for_component(
                name, BaseDataGenerator.get_data_generator
            )
            if data_generator_config:
                data_generators_section.update(data_generator_config)
        if data_generators_section:
            dataset_section["data_generators"] = data_generators_section
    return dataset_section


def generate_impprover_config(improver_name) -> Optional[Dict[str, Any]]:
    """Generate the improved section of the experiment config."""
    return get_config_for_component(
        improver_name, BaseCombinationImprover.get_combination_improver
    )


def generate_variations_section(wrapper_configs) -> str:
    """Generate the variations section."""
    if not wrapper_configs:
        return """
        # variations:
        #   - name: wrapper_name
        #     variations:
        #       - value_type: str
        #         value: "example_variation"
        #         instantiated_value: "example_variation"
        #     generator_name: example_generator_name
        #     generator_config:
        #       number_of_variations: 5
        #       output_path: /path/to/output
        """

    variations_list = []
    for wrapper_config in wrapper_configs:
        wrapper_dict = wrapper_config.asdict()
        if wrapper_config.generator_name:
            wrapper_generator_cls = BaseVariationGenerator.get_variation_generator(
                wrapper_config.generator_name
            )
            if wrapper_generator_cls:
                default_config = get_default_config(wrapper_generator_cls)
                if default_config:
                    wrapper_dict["generator_config"] = default_config
        variations_list.append(wrapper_dict)
    res = "\nvariations:\n"
    res += yaml.safe_dump(
        variations_list,
        default_flow_style=False,
        allow_unicode=True,
        indent=2
    )
    return res


from enum import Enum

import yaml


# Refactored main function
def generate_experiment_config_yaml(
    custom_function: str,
    source_type: str = "dataset",
    evaluator_names: Optional[List[str]] = None,
    reader_name: Optional[str] = None,
    improver_name: Optional[str] = None,
    wrapper_names: Optional[List[str]] = None,
    data_generator_names: Optional[List[str]] = None,
    selection_strategy_name: Optional[str] = None,
    wrapper_configs: Optional[List[WrapperConfig]] = None,
    custom_reader: Optional[Dict[str, Dict[str, Any]]] = None,
    custom_wrappers: Optional[Dict[str, Dict[str, Any]]] = None,
    custom_evaluators: Optional[Dict[str, Dict[str, Any]]] = None,
    custom_data_generators: Optional[Dict[str, Dict[str, Any]]] = None,
    custom_variation_generators: Optional[Dict[str, Dict[str, Any]]] = None,
    custom_selection_strategy: Optional[Dict[str, Dict[str, Any]]] = None,
    custom_improver: Optional[Dict[str, Dict[str, Any]]] = None
) -> str:

    experiment_config = {
        "description":
        "Generated experiment config",
        "dataset":
        generate_dataset_section(
            source_type, reader_name, data_generator_names
        ),
        "custom_function":
        custom_function
    }

    if improver_name:
        config = generate_impprover_config(improver_name)
        if config:
            experiment_config["improver"] = config

    # Add selection strategy
    if selection_strategy_name:
        experiment_config["selection_strategy"] = get_config_for_component(
            selection_strategy_name, SelectionStrategy.get_strategy
        )

    # Add custom sections if they exist
    custom_sections = {
        "custom_reader": custom_reader,
        "custom_improver": custom_improver,
        "custom_wrappers": custom_wrappers,
        "custom_evaluators": custom_evaluators,
        "custom_data_generators": custom_data_generators,
        "custom_variation_generators": custom_variation_generators,
        "custom_selection_strategies": custom_selection_strategy
    }
    for section_name, section_content in custom_sections.items():
        if section_content:
            experiment_config[section_name] = section_content

    # Process evaluators
    if evaluator_names:
        evaluators_section = []
        for name in evaluator_names:
            evaluator_config = get_config_for_component(
                name, BaseEvaluator.get_evaluator
            )
            if evaluator_config:
                evaluator_config["name"] = name  # Add the name field
                evaluators_section.append(evaluator_config)
        experiment_config["evaluators"] = evaluators_section

    # Process wrappers
    if wrapper_names:
        wrappers_section = {}
        for name in wrapper_names:
            wrapper_config = get_config_for_component(
                name, BaseWrapper.get_wrapper
            )
            wrappers_section.update(wrapper_config)
        experiment_config["wrapper_configs"] = wrappers_section

    experiment_config = recursive_asdict(experiment_config)
    yaml_string = yaml.safe_dump(
        experiment_config, default_flow_style=False, allow_unicode=True
    )

    if not evaluator_names:
        yaml_string += "\n# evaluators: []\n"
    if not wrapper_names:
        yaml_string += "\n# wrapper_configs: {}\n"

    yaml_string += generate_variations_section(wrapper_configs)
    yaml_string = "# This is a generated template. Modify the values as needed.\n\n" + yaml_string

    return yaml_string
