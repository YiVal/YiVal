from collections import defaultdict
from itertools import product
from typing import Any, Dict, Iterator, List, Optional, Union

from ..schemas.experiment_config import ExperimentConfig
from ..schemas.varation_generator_configs import BaseVariationGeneratorConfig
from ..variation_generators.base_variation_generator import (
    BaseVariationGenerator,
)


class ExperimentState:
    """
    Represents the state for managing experiment variations.

    This class maintains the state of active experiments and their variations.

    Attributes:
        active (bool): Indicates if the experiment is currently active.
        current_variations (Dict[str, List[Any]]): A dictionary where keys are
        experiment names and values are lists of variations.
        counters (Dict[str, int]): A counter for each experiment name to rotate through
        its variations.

    Methods:
        get_next_variation(name: str) -> Optional[Any]:
            Depending on the global ExperimentState's activity status, retrieves the
            next variation for the associated experiment name. If the state is inactive
            or no variations are found, returns None.
    """

    _shared_instance = None

    @staticmethod
    def get_instance():
        if ExperimentState._shared_instance is None:
            ExperimentState._shared_instance = ExperimentState()
        return ExperimentState._shared_instance

    def __init__(self) -> None:
        self.active: bool = False
        self.current_variations: Dict[str, List[Any]] = {}
        self.counters: Dict[str, int] = defaultdict(int)
        self.config: Optional[ExperimentConfig] = None

    def get_next_variation(self, name: str) -> Optional[Any]:
        variations = self.current_variations.get(name, [])
        if self.counters[name] < len(variations):
            variation = variations[self.counters[name]]
            self.counters[name] += 1
            return variation
        return None

    def get_all_variation_combinations(self) -> List[Dict[str, Any]]:
        """
        Returns a list of dictionaries where each dictionary 
        represents a unique combination of variations.
        """
        all_variations = []
        for name, variations in self.current_variations.items():
            all_variations.append([(name, variation)
                                   for variation in variations])
        combinations = []
        for combo in product(*all_variations):
            combo_dict = {name: variation for name, variation in combo}
            combinations.append(combo_dict)
        return combinations

    def initialize_variations_from_config(self) -> None:
        """
        Initializes the experiment variations using the provided ExperimentConfig.
        """
        if self.config and self.config.variations:
            for wrapper_config in self.config.variations:
                if not isinstance(wrapper_config, dict):
                    wrapper_config = wrapper_config.asdict()  # type: ignore
                if "variations" in wrapper_config:  # type: ignore
                    variations = [
                        var_variation["instantiated_value"] for var_variation
                        in wrapper_config["variations"]  # type: ignore
                    ]
                    self.set_variations_for_experiment(
                        wrapper_config["name"],  # type: ignore
                        variations
                    )
                if "generator_name" in wrapper_config:  # type: ignore
                    generator_cls = BaseVariationGenerator.get_variation_generator(
                        wrapper_config["generator_name"]  # type: ignore
                    )
                    config_cls = BaseVariationGenerator.get_config_class(
                        wrapper_config["generator_name"]  # type: ignore
                    )
                    if generator_cls:
                        if config_cls:
                            if "generator_config" in wrapper_config:  # type: ignore
                                if isinstance(
                                    wrapper_config["generator_config"
                                                   ],  # type: ignore
                                    dict
                                ):
                                    config_data = wrapper_config[  # type: ignore
                                        "generator_config"]
                                else:
                                    config_data = wrapper_config[  # type: ignore
                                        "generator_config"].asdict()
                                config_instance = config_cls(**config_data)
                            else:
                                config_instance = config_cls()
                            generator_instance = generator_cls(config_instance)
                        else:
                            generator_instance = generator_cls(
                                BaseVariationGeneratorConfig()
                            )
                        vs = []
                        for vars in generator_instance.generate_variations():
                            for var in vars:
                                vs.append(var.instantiated_value)
                        self.set_variations_for_experiment(
                            wrapper_config["name"],  # type: ignore
                            vs
                        )

    def set_variations_for_experiment(
        self, name: str, variations: Union[List[Any], Iterator[Any]]
    ) -> None:
        existing_variations = self.current_variations.get(name, [])
        existing_variations.extend(variations)
        self.current_variations[name] = existing_variations

    def clear_variations_for_experiment(self) -> None:
        self.current_variations.clear()

    def set_experiment_config(self, config: Any) -> None:
        if isinstance(config, dict):
            self.config = ExperimentConfig(**config)
        else:
            self.config = config
        self.initialize_variations_from_config()

    def set_specific_variation(self, name: str, variation: Any) -> None:
        """
        Sets a specific variation for an experiment without cycling through the variations.
        """
        self.current_variations[name] = [variation]
        self.counters[name] = 0
