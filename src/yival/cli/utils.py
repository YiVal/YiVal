from enum import Enum
from typing import Any, Dict, List, Optional, Type

import yaml

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


def generate_experiment_config_yaml(
    custom_function: str,
    source_type: str = "dataset",
    evaluator_names: Optional[List[str]] = None,
    reader_name: Optional[str] = None,
    wrapper_names: Optional[List[str]] = None,
    data_generator_names: Optional[List[str]] = None,
    selection_strategy_name: Optional[str] = None,
    wrapper_configs: Optional[List[WrapperConfig]] = None,
    custom_reader: Optional[Dict[str, Dict[str, Any]]] = None,
    custom_wrappers: Optional[Dict[str, Dict[str, Any]]] = None,
    custom_evaluators: Optional[Dict[str, Dict[str, Any]]] = None,
    custom_data_generators: Optional[Dict[str, Dict[str, Any]]] = None,
    custom_variation_generators: Optional[Dict[str, Dict[str, Any]]] = None,
    custom_selection_strategy: Optional[Dict[str, Dict[str, Any]]] = None
) -> str:

    def get_default_config(
        component_class: Type[Any]
    ) -> Optional[Dict[str, Any]]:
        """Retrieve the default configuration of a component, if available."""
        default = getattr(component_class, "default_config", None)
        if default:
            return default.__dict__
        return None

    dataset_section: Dict[str, Any] = {
        "source_type": source_type,
    }
    if source_type == "dataset":
        dataset_section["file_path"] = "/path/to/file_path"
    if reader_name and source_type == "dataset":
        dataset_section["reader"] = reader_name
        reader_cls = BaseReader.get_reader(reader_name)
        if reader_cls:
            default_config = get_default_config(reader_cls)
            if default_config:
                dataset_section["reader_config"] = default_config
    if data_generator_names and source_type == "machine_generated":
        data_generators_section = {}
        for name in data_generator_names:
            data_generator_cls = BaseDataGenerator.get_data_generator(name)
            if data_generator_cls:
                default_config = get_default_config(data_generator_cls)
                if default_config:
                    data_generators_section[name] = default_config
        if data_generators_section:
            dataset_section["data_generators"] = data_generators_section

    experiment_config: Dict[Any, Any] = {
        "description": "Generated experiment config",
        "dataset": dataset_section,
    }

    selection_strategy_section = {}
    if selection_strategy_name:
        strategy_cls = SelectionStrategy.get_strategy(selection_strategy_name)
        if strategy_cls:
            default_config = get_default_config(strategy_cls)
            if default_config:
                selection_strategy_section[selection_strategy_name
                                           ] = default_config

    if selection_strategy_section:
        experiment_config["selection_strategy"] = selection_strategy_section

    if custom_reader:
        experiment_config["custom_reader"] = custom_reader

    if custom_wrappers:
        experiment_config["custom_wrappers"] = custom_wrappers

    if custom_evaluators:
        experiment_config["custom_evaluators"] = custom_evaluators

    if custom_data_generators:
        experiment_config["custom_data_generators"] = custom_data_generators

    if custom_variation_generators:
        experiment_config["custom_variation_generators"
                          ] = custom_variation_generators

    if custom_selection_strategy:
        experiment_config["custom_selection_strategies"
                          ] = custom_selection_strategy

    evaluators_section = []
    if evaluator_names:
        for name in evaluator_names:
            evaluator_cls = BaseEvaluator.get_evaluator(name)
            if evaluator_cls:
                default_config = get_default_config(evaluator_cls)
                if default_config:
                    default_config["name"] = name  # Add the name field
                    evaluators_section.append(default_config)

    if wrapper_names:
        wrappers_section = {}
        for name in wrapper_names:
            wrapper_cls = BaseWrapper.get_wrapper(name)
            if wrapper_cls:
                default_config = get_default_config(wrapper_cls)
                wrappers_section[name
                                 ] = default_config if default_config else {}
        experiment_config["wrapper_configs"] = wrappers_section

    if evaluator_names:
        experiment_config["evaluators"] = evaluators_section

    experiment_config["custom_function"] = custom_function

    experiment_config = recursive_asdict(experiment_config)
    yaml_string = yaml.safe_dump(
        experiment_config, default_flow_style=False, allow_unicode=True
    )

    if not evaluator_names:
        yaml_string += "\n# evaluators: []\n"
    if not wrapper_names:
        yaml_string += "\n# wrapper_configs: {}\n"

    variations_section = """
    # Variations allow for dynamic content during experiments.
    # They are identified by a globally unique name. For example, in your code,
    # you might reference a variation by its name, like:
    # variation = StringWrapper("hello", 'test_experiment')
    # In this config, you would define the variations associated with that name.
    """

    if wrapper_configs:
        variations_list = []
        for wrapper_config in wrapper_configs:
            wrapper_dict = wrapper_config.asdict()
            # Check if there's a generator config, and if so, convert it to dict as well
            if wrapper_config.generator_name:
                wrapper_generator_cls = BaseVariationGenerator.get_variation_generator(
                    wrapper_config.generator_name
                )
                if wrapper_generator_cls:
                    default_config = get_default_config(wrapper_generator_cls)
                    if default_config:
                        wrapper_dict["generator_config"] = default_config
            variations_list.append(wrapper_dict)
        yaml_string += "\nvariations:\n"
        yaml_string += yaml.safe_dump(
            variations_list,
            default_flow_style=False,
            allow_unicode=True,
            indent=2
        )
        # variations_section += yaml.safe_dump({"variations": variations_list},
        #                                     default_flow_style=False,
        #                                     allow_unicode=True)
    else:
        variations_section += """
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

    yaml_string += variations_section
    yaml_string = "# This is a generated template. Modify the values as needed.\n\n" + yaml_string

    return yaml_string
