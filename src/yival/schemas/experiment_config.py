"""
Module for experiment configuration structures.

This module provides data structures to capture configurations required to run
an experiment.
"""
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union

from PIL import Image

from .combination_enhancer_configs import BaseCombinationEnhancerConfig
from .common_structures import InputData
from .dataset_config import DatasetConfig
from .evaluator_config import (
    ComparisonEvaluatorConfig,
    EvaluatorConfig,
    EvaluatorOutput,
    GlobalEvaluatorConfig,
)
from .selector_strategies import BaseConfig, SelectionOutput
from .trainer_configs import BaseTrainerConfig
from .varation_generator_configs import BaseVariationGeneratorConfig
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

    """

    name: str
    variations: Optional[List[WrapperVariation]] = None
    generator_name: Optional[str] = None
    generator_config: Optional[BaseVariationGeneratorConfig] = None

    def asdict(self) -> Dict[str, Any]:
        return {
            "name":
            self.name,
            "variations":
            [var.asdict()
             for var in self.variations] if self.variations else None,
            "generator_name":
            self.generator_name,
            "generator_config":
            self.generator_config.asdict() if self.generator_config else None
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
    - scale (Tuple[float, float]): Minimum and maximum value of the rating
            scale.
    """

    aspect: str
    rating: float
    scale: Tuple[float, float] = (1.0, 5.0)  # Default scale from 1 to 5

    def asdict(self):
        return asdict(self)


@dataclass
class HumanRatingConfig:
    name: str
    instructions: str
    scale: Tuple[float, float] = (1.0, 5.0)

    def asdict(self):
        return asdict(self)


@dataclass
class ExperimentConfig:

    # Required configurations
    description: str
    dataset: DatasetConfig
    # Optional configurations with default values
    custom_function: Optional[str] = None
    variations: Optional[List[WrapperConfig]] = None
    selection_strategy: Optional[Dict[str, BaseConfig]] = None
    wrapper_configs: Optional[Dict[str, BaseWrapperConfig]] = None
    combinations_to_run: Optional[List[Tuple[str, Any]]] = None
    evaluators: Optional[List[Union[EvaluatorConfig, ComparisonEvaluatorConfig,
                                    GlobalEvaluatorConfig]]] = None
    enhancer: Optional[BaseCombinationEnhancerConfig] = None
    trainer: Optional[BaseTrainerConfig] = None
    output: Optional[OutputConfig] = None
    human_rating_configs: Optional[List[HumanRatingConfig]] = None
    existing_experiment_path: Optional[str] = None
    version: Optional[str] = None
    output_parser: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    custom_reader: Optional[Dict[str, Dict[str, Any]]] = None
    custom_combination_enhancer: Optional[Dict[str, Dict[str, Any]]] = None
    custom_data_generators: Optional[Dict[str, Dict[str, Any]]] = None
    custom_wrappers: Optional[Dict[str, Dict[str, Any]]] = None
    custom_evaluators: Optional[Dict[str, Dict[str, Any]]] = None
    custom_variation_generators: Optional[Dict[str, Dict[str, Any]]] = None
    custom_selection_strategies: Optional[Dict[str, Dict[str, Any]]] = None
    custom_enhancers: Optional[Dict[str, Dict[str, Any]]] = None

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

        # Note: For the custom_reader, custom_wrappers, custom_evaluators
        # attributes, you'd need additional logic if their nested dictionaries
        # also contain objects that need to be converted using asdict.

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
      A dictionary where keys are evaluator names and values are dictionaries
      mapping metric names to their values.
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
class Context:
    """
    Custom function context that will be used for evlaution
    """
    text_context: Dict[str, str] = field(default_factory=dict)


@dataclass
class MultimodalOutput:
    """
    Multimodal output that can include a string, a PIL Image, or both.

    Attributes:
    - text_output (str): Text output for this example.
    - image_output (PIL.Image.Image): Image output for this example.
    """
    text_output: Optional[str] = None
    image_output: Optional[List[Image.Image]] = None
    video_output: Optional[List[str]] = None
    context: Optional[Context] = None

    def asdict(self) -> Dict[str, Any]:
        return {
            "text_output": self.text_output,
            "image_output": "PIL Image List" if self.image_output else
            None,  # You might want to serialize the image differently
            "video_output": "video URL List" if self.video_output else None
        }


@dataclass
class ExperimentResult:
    """
    Result for a single example based on a specific combination of active
    variations across wrappers.

    Attributes:
    - combination (Dict[str, str]): The combination of wrapper names and their
      active variation_ids for this example.
    - raw_output (Any): Raw output for this example. Support str and PILimage
    - latency (float): Latency for producing the output for this example
      (in milliseconds or appropriate unit).
    - token_usage (int): Number of tokens used for this example.
    - evaluator_outputs (List[EvaluatorOutput]): Evaluator outputs for this
      example.
    - human_rating (Optional[HumanRating]): Human rating for this example.
    - intermediate_logs (List[str]): Logs captured during the experiment.
    """

    input_data: InputData
    combination: Dict[str, str]
    raw_output: MultimodalOutput
    latency: float
    token_usage: int
    evaluator_outputs: Optional[List[EvaluatorOutput]] = None
    intermediate_logs: Optional[List[str]] = None

    def asdict(self) -> Dict[str, Any]:
        return {
            "input_data":
            self.input_data.asdict(),
            "combination":
            self.combination,
            "raw_output":
            self.raw_output.asdict(),
            "latency":
            self.latency,
            "token_usage":
            self.token_usage,
            "evaluator_outputs":
            [eo.asdict() for eo in self.evaluator_outputs]
            if self.evaluator_outputs else None,
            "intermediate_logs":
            self.intermediate_logs
        }


@dataclass
class GroupedExperimentResult:
    group_key: str
    experiment_results: List[ExperimentResult]
    grouped_evaluator_outputs: Optional[List[EvaluatorOutput]] = None

    def asdict(self) -> Dict[str, Any]:
        return {
            "group_key":
            self.group_key,
            "experiment_results":
            [er.asdict() for er in self.experiment_results],
            "evaluator_outputs":
            [eo.asdict() for eo in self.grouped_evaluator_outputs]
            if self.grouped_evaluator_outputs else None
        }


@dataclass
class CombinationAggregatedMetrics:
    combo_key: str
    experiment_results: List[ExperimentResult]
    aggregated_metrics: Dict[str, List[Metric]]
    average_token_usage: Optional[float] = None
    average_latency: Optional[float] = None
    combine_evaluator_outputs: Optional[List[EvaluatorOutput]] = None

    def asdict(self) -> Dict[str, Any]:
        return {
            "combo_key":
            self.combo_key,
            "experiment_results":
            [er.asdict() for er in self.experiment_results],
            "aggregated_metrics": {
                k: [m.asdict() for m in v]
                for k, v in self.aggregated_metrics.items()
            },
            "average_token_usage":
            self.average_token_usage,
            "average_latency":
            self.average_latency,
            "evaluator_outputs":
            [eo.asdict() for eo in self.combine_evaluator_outputs]
            if self.combine_evaluator_outputs else None
        }


@dataclass
class FunctionMetadata:
    description: str
    parameters: List[Tuple[str,
                           Optional[str]]]  # [(param_name, description), ...]


@dataclass
class EnhancerOutput:
    """
    Represents the outputs related to the "enhancer" component of the
    experiment.
    
    The enhancer's role is to enhance or optimize certain aspects of the
    experiment. 
    This dataclass captures the results, metrics, and decisions made by the
    enhancer.

    Attributes:
        group_experiment_results (List[GroupedExperimentResult]): List of
        grouped results after enhancement.
        combination_aggregated_metrics (List[CombinationAggregatedMetrics]):
        Aggregated metrics post-enhancement.
        original_best_combo_key (str): The best combination key before the
        enhancer made optimizations.
        selection_output (Optional[SelectionOutput]): Output from the selection

    """
    group_experiment_results: List[GroupedExperimentResult]
    combination_aggregated_metrics: List[CombinationAggregatedMetrics]
    original_best_combo_key: str
    selection_output: Optional[SelectionOutput] = None


@dataclass
class TrainerOutput:
    train_logs: List[str]


@dataclass
class Experiment:
    """
    Represents the entirety of an experiment run.

    This dataclass encapsulates the results, metrics, and configurations used
    and generated during the experiment. 
    It is a comprehensive view of everything related to a specific experiment
    run.

    Attributes:
        group_experiment_results (List[GroupedExperimentResult]): List of
        results grouped by test cases.
        combination_aggregated_metrics (List[CombinationAggregatedMetrics]):
        Metrics aggregated for specific combinations.
        selection_output (Optional[SelectionOutput]): Output from the
        selection strategy. enhancer_output (Optional[enhancerOutput]):
        Output from the enhancer component, if used.

    """
    group_experiment_results: List[GroupedExperimentResult]
    combination_aggregated_metrics: List[CombinationAggregatedMetrics]
    enable_custom_func: bool = False
    selection_output: Optional[SelectionOutput] = None
    enhancer_output: Optional[EnhancerOutput] = None

    def asdict(self) -> Dict[str, Any]:
        return {
            "group_experiment_results":
            [ger.asdict() for ger in self.group_experiment_results],
            "combination_aggregated_metrics":
            [cam.asdict() for cam in self.combination_aggregated_metrics]
        }
