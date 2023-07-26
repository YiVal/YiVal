from typing import Any, Dict, List, Optional, Type

import yaml

from ..data.base_reader import BaseReader
from ..evaluators.base_evaluator import BaseEvaluator
from ..schemas.experiment_config import WrapperConfig
from ..wrappers.base_wrapper import BaseWrapper


def generate_experiment_config_yaml(
    source_type: str = "DATASET",
    evaluator_names: Optional[List[str]] = None,
    reader_name: Optional[str] = None,
    wrapper_names: Optional[List[str]] = None,
    wrapper_configs: Optional[List[WrapperConfig]] = None
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
    if reader_name:
        dataset_section["reader"] = reader_name
        reader_cls = BaseReader.get_reader(reader_name)
        if reader_cls:
            default_config = get_default_config(reader_cls)
            if default_config:
                dataset_section["config"] = default_config

    evaluators_section = {}
    if evaluator_names:
        for name in evaluator_names:
            evaluator_cls = BaseEvaluator.get_evaluator(name)
            if evaluator_cls:
                default_config = get_default_config(evaluator_cls)
                if default_config:
                    if "evaluator_type" in default_config:
                        default_config["evaluator_type"] = str(
                            default_config["evaluator_type"]
                        )
                    if "matching_technique" in default_config:
                        default_config["matching_technique"] = str(
                            default_config["matching_technique"]
                        )
                evaluators_section[name] = {
                    "config": default_config if default_config else {}
                }

    wrappers_section = {}
    if wrapper_names:
        for name in wrapper_names:
            wrapper_cls = BaseWrapper.get_wrapper(name)
            if wrapper_cls:
                default_config = get_default_config(wrapper_cls)
                wrappers_section[name] = {
                    "config": default_config if default_config else {}
                }

    experiment_config = {
        "description": "Generated experiment config",
        "dataset": dataset_section,
    }

    if evaluator_names:
        experiment_config["evaluators"] = evaluators_section

    if wrapper_names:
        experiment_config["wrapper_configs"] = wrappers_section

    yaml_string = yaml.safe_dump(
        experiment_config, default_flow_style=False, allow_unicode=True
    )

    if not evaluator_names:
        yaml_string += "\n# evaluators: []\n"
    if not wrapper_names:
        yaml_string += "\n# wrapper_configs: []\n"

    variations_section = """
# Variations allow for dynamic content during experiments.
# They are identified by a globally unique name. For example, in your code,
# you might reference a variation by its name, like:
# variation = StringWrapper("hello", 'test_experiment')
# In this config, you would define the variations associated with that name, e.g.
"""
    if wrapper_configs:
        variations_list = []
        for wrapper_config in wrapper_configs:
            wrapper_dict = wrapper_config.asdict()
            variations_list.append(wrapper_dict)

        variations_section += yaml.safe_dump({"variations": variations_list},
                                             default_flow_style=False,
                                             allow_unicode=True)
    else:
        variations_section += """
# variations:
#   - name: wrapper_name
#     variations:
#       - value_type: str
#         value: "example_variation"
#         instantiated_value: "example_variation"
"""

    yaml_string += variations_section
    yaml_string = "# This is a generated template. Modify the values as needed.\n\n" + yaml_string

    return yaml_string
