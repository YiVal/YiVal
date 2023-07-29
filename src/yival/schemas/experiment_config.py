"""
Module for experiment configuration structures.

This module provides data structures to capture configurations required to run an
experiment.
"""
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union

from .common_structures import InputData
from .dataset_config import DatasetConfig
from .evaluator_config import (
    ComparisonEvaluatorConfig,
    EvaluatorConfig,
    EvaluatorOutput,
)
from .wrapper_configs import BaseWrapperConfig

# Registry for supported custom classes
# TODO Fix it, this is not working right now
CLASS_REGISTRY: Dict[str, Type] = {
    # "ClassA": ClassA
}


@dataclass
class WrapperVariation:
    """
    Represents a variation within a wrapper.
    The value can be any type, but typical usages might include strings, 
    numbers, configuration dictionaries, or even custom class configurations.
    """

    value_type: str  # e.g., "string", "int", "float", "ClassA", ...
    value: Any  # The actual value or parameters to initialize a value
    instantiated_value: Any = field(init=False)
    variation_id: Optional[str] = None

    def asdict(self):
        return asdict(self)

    def __post_init__(self):
        self.instantiated_value = self.instantiate()

    def instantiate(self) -> Any:
        """
        Returns an instantiated value based on value_type and params.
        """
        if self.value_type in ["str", "int", "float", "bool"]:
            return eval(self.value_type)(
                self.value
            )  # Use eval to convert string type to actual type
        elif self.value_type in CLASS_REGISTRY:
            return CLASS_REGISTRY[self.value_type](**self.value)
        else:
            raise ValueError(f"Unsupported value_type: {self.value_type}")


@dataclass
class WrapperConfig():
    """
    Configuration for each individual wrapper used in the experiment.

    Attributes:
    - name (str): Name of the wrapper.
    - variations (List[WrapperVariation]): Variations for this wrapper.
    """

    name: str
    variations: List[WrapperVariation]

    def asdict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "variations": [var.asdict() for var in self.variations]
        }


@dataclass
class OutputConfig:
    """
    Configuration for experiment output.

    Attributes:
    - path (str): Path where the experiment output should be saved.
    - formatter (Callable): Function to format the output.
    """

    path: str
    formatter: Callable


@dataclass
class ComparisonOutput:
    """
    Result of a comparison evaluation.

    Attributes:
    - better_output (str): Name of the wrapper that produced the better output.
    - reason (str): Reason or metric based on which the decision was made.
    """

    better_output: str
    reason: str


@dataclass
class HumanRating:
    """
    Human rating for an output.

    Attributes:
    - aspect (str): Aspect being rated.
    - rating (float): Rating value.
    - scale (Tuple[float, float]): Minimum and maximum value of the rating scale.
    """

    aspect: str
    rating: float
    scale: Tuple[float, float] = (1.0, 5.0)  # Default scale from 1 to 5

    def asdict(self):
        return asdict(self)


@dataclass
class HumanRatingConfig:
    """
    Configuration for human rating.

    Attributes:
    - aspects (List[str]): List of aspects to rate.
    - scale (Tuple[float, float]): Minimum and maximum value of the rating scale.
    """

    aspects: List[str]
    scale: Tuple[float, float] = (1.0, 5.0)

    def asdict(self):
        return asdict(self)


@dataclass
class ExperimentConfig:
    """
    Configuration for running an experiment.

    Attributes:
    - description (str): Description of the experiment.
    - variations (List[WrapperConfig]): List of variations configurations.
    - dataset (DatasetConfig): Dataset configuration.
    - wrapper_configs (List[BaseWrapperConfig]): List of wrapper configurations.
    - combinations_to_run (Optional[List[Tuple[str, Any]]]): List of combinations to
      run.
      Each tuple represents a (group_name, variation) pair.
    - evaluators (Optional[List[Union[EvaluatorConfig, ComparisonEvaluatorConfig]]]):
      List of evaluator configurations.
    - output (Optional[OutputConfig]): Output configuration.

    - existing_experiment_path (Optional[str]): Path to an existing experiment for
      incremental experiments or comparisons.
    - version (Optional[str]): Version or timestamp for the experiment.
    - output_parser (Optional[str]): Class name of the std output parser to use.
    - metadata (Dict[str, Any]): Additional metadata related to the experiment.
    - custom_reader (Dict[str, Dict[str, Any]]): Custom reader and configurations.
    - custom_data_generator (Dict[str, Dict[str, Any]]): Custom data generator and configurations.
    - custom_wrappers (Dict[str, Dict[str, Any]]): Custom wrapper and configurations.
    - custom_evaluators (Dict[str, Dict[str, Any]]): Custom evaluator and configurations.
    """

    # Required configurations
    description: str
    variations: List[WrapperConfig]
    dataset: DatasetConfig
    custom_function: str
    # Optional configurations with default values
    wrapper_configs: Optional[Dict[str, BaseWrapperConfig]] = None
    combinations_to_run: Optional[List[Tuple[str, Any]]] = None
    evaluators: Optional[List[Union[EvaluatorConfig,
                                    ComparisonEvaluatorConfig]]] = None
    output: Optional[OutputConfig] = None
    human_rating_configs: Optional[List[HumanRatingConfig]] = None
    existing_experiment_path: Optional[str] = None
    version: Optional[str] = None
    output_parser: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    custom_reader: Optional[Dict[str, Dict[str, Any]]] = None
    custom_data_generator: Optional[Dict[str, Dict[str, Any]]] = None
    custom_wrappers: Optional[Dict[str, Dict[str, Any]]] = None
    custom_evaluators: Optional[Dict[str, Dict[str, Any]]] = None

    def asdict(self) -> Dict[str, Any]:
        # Convert the dataclass instance to a dictionary
        result = asdict(self)

        # If any attributes have their own asdict methods, apply them
        if self.variations:
            result["variations"] = [
                v.asdict() for v in self.variations if hasattr(v, 'asdict')
            ]
        if self.dataset and hasattr(self.dataset, 'asdict'):
            result["dataset"] = self.dataset.asdict()
        if self.wrapper_configs:
            result["wrapper_configs"] = {
                k: v.asdict()
                for k, v in self.wrapper_configs.items()
                if hasattr(v, 'asdict')
            }
        if self.evaluators:
            result["evaluators"] = [
                e.asdict() for e in self.evaluators if hasattr(e, 'asdict')
            ]
        if self.output and hasattr(self.output, 'asdict'):
            result["output"] = self.output.asdict()
        if self.human_rating_configs:
            result["human_rating_configs"] = [
                h.asdict() for h in self.human_rating_configs
                if hasattr(h, 'asdict')
            ]

        # Note: For the custom_reader, custom_wrappers, custom_evaluators attributes,
        # you'd need additional logic if their nested dictionaries also contain objects
        # that need to be converted using asdict.

        return result


@dataclass
class Metric:
    """
    Represents a metric calculated from evaluator outputs.

    Attributes:
    - name (str): Name of the metric (e.g., "accuracy").
    - value (float): Calculated value of the metric.
    - description (Optional[str]): Description or details about the metric.
    """
    name: str
    value: float
    description: Optional[str] = None

    def asdict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "description": self.description
        }


@dataclass
class ExperimentSummary:
    """
    Represents the summary of an entire experiment.

    Attributes:
    - aggregated_metrics (Dict[str, Dict[str, Metric]]): 
      A dictionary where keys are evaluator names and values are dictionaries mapping metric names to their values.
    - ... (other summary attributes)
    """
    aggregated_metrics: Dict[str, Dict[str, Metric]]

    def asdict(self) -> Dict[str, Any]:
        return {
            "aggregated_metrics": {
                k: {
                    mk: mv.asdict()
                    for mk, mv in v.items()
                }
                for k, v in self.aggregated_metrics.items()
            }
        }


@dataclass
class ExperimentResult:
    """
    Result for a single example based on a specific combination of active variations
    across wrappers.

    Attributes:
    - combination (Dict[str, str]): The combination of wrapper names and their active
      variation_ids for this example.
    - raw_output (str): Raw output for this example.
    - latency (float): Latency for producing the output for this example
      (in milliseconds or appropriate unit).
    - token_usage (int): Number of tokens used for this example.
    - evaluator_outputs (List[EvaluatorOutput]): Evaluator outputs for this example.
    - human_rating (Optional[HumanRating]): Human rating for this example.
    - intermediate_logs (List[str]): Logs captured during the experiment.
    """

    input_data: InputData
    combination: Dict[str, str]
    raw_output: str
    latency: float
    token_usage: int
    evaluator_outputs: Optional[List[EvaluatorOutput]] = None
    human_rating: Optional[HumanRating] = None
    intermediate_logs: Optional[List[str]] = None

    def asdict(self) -> Dict[str, Any]:
        return {
            "input_data":
            self.input_data.asdict(),
            "combination":
            self.combination,
            "raw_output":
            self.raw_output,
            "latency":
            self.latency,
            "token_usage":
            self.token_usage,
            "evaluator_outputs":
            [eo.asdict() for eo in self.evaluator_outputs]
            if self.evaluator_outputs else None,
            "human_rating":
            self.human_rating.asdict() if self.human_rating else None,
            "intermediate_logs":
            self.intermediate_logs
        }


@dataclass
class GroupedExperimentResult:
    group_key: str
    experiment_results: List[ExperimentResult]
    evaluator_outputs: Optional[List[EvaluatorOutput]] = None

    def asdict(self) -> Dict[str, Any]:
        return {
            "group_key":
            self.group_key,
            "experiment_results":
            [er.asdict() for er in self.experiment_results],
            "evaluator_outputs":
            [eo.asdict() for eo in self.evaluator_outputs]
            if self.evaluator_outputs else None
        }


@dataclass
class CombinationAggregatedMetrics:
    combo_key: str
    experiment_results: List[ExperimentResult]
    aggregated_metrics: Dict[str, List[Metric]]
    average_token_usage: Optional[float] = None
    average_latency: Optional[float] = None

    def asdict(self) -> Dict[str, Any]:
        return {
            "combo_key": self.combo_key,
            "experiment_results":
            [er.asdict() for er in self.experiment_results],
            "aggregated_metrics": {
                k: [m.asdict() for m in v]
                for k, v in self.aggregated_metrics.items()
            },
            "average_token_usage": self.average_token_usage,
            "average_latency": self.average_latency
        }


@dataclass
class FunctionMetadata:
    description: str
    parameters: List[Tuple[str,
                           Optional[str]]]  # [(param_name, description), ...]


@dataclass
class Experiment:
    """
    Represents an entire experiment.

    """
    group_experiment_results: List[GroupedExperimentResult]
    combination_aggregated_metrics: List[CombinationAggregatedMetrics]

    def asdict(self) -> Dict[str, Any]:
        return {
            "group_experiment_results":
            [ger.asdict() for ger in self.group_experiment_results],
            "combination_aggregated_metrics":
            [cam.asdict() for cam in self.combination_aggregated_metrics]
        }
