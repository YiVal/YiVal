"""
Module for experiment configuration structures.

This module provides data structures to capture configurations required to run an
experiment.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from .common_structures import InputData
from .dataset_config import DatasetConfig
from .evaluator_config import (
    ComparisonEvaluatorConfig,
    EvaluatorConfig,
    EvaluatorOutput,
)


@dataclass
class WrapperVariation:
    """
    Represents a variation within a wrapper.
    The value can be any type, but typical usages might include strings,
    numbers, or configuration dictionaries.
    """

    value: Any
    variation_id: Optional[str] = None


@dataclass
class WrapperConfig:
    """
    Configuration for each individual wrapper used in the experiment.

    Attributes:
    - name (str): Name of the wrapper.
    - variations (List[WrapperVariation]): Variations for this wrapper.
    """

    name: str
    variations: List[WrapperVariation]


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
    evaluator_outputs: List[EvaluatorOutput]
    human_rating: Optional[HumanRating] = None
    intermediate_logs: List[str] = field(default_factory=list)


@dataclass
class ExperimentConfig:
    """
    Configuration for running an experiment.

    Attributes:
    - description (str): Description of the experiment.
    - wrappers (List[WrapperConfig]): List of wrapper configurations.
    - dataset (DatasetConfig): Dataset configuration.

    - combinations_to_run (Optional[List[Tuple[str, Any]]]): List of combinations to
      run.
      Each tuple represents a (group_name, variation) pair.
    - evaluators (Optional[List[Union[EvaluatorConfig, ComparisonEvaluatorConfig]]]):
      List of evaluator configurations.
    - output (Optional[OutputConfig]): Output configuration.

    - human_ratings (List[HumanRating]): List of human ratings for the experiment.
    - existing_experiment_path (Optional[str]): Path to an existing experiment for
      incremental experiments or comparisons.
    - version (Optional[str]): Version or timestamp for the experiment.
    - output_parser (Optional[str]): Class name of the std output parser to use.
    - metadata (Dict[str, Any]): Additional metadata related to the experiment.
    """

    # Required configurations
    description: str
    wrappers: List[WrapperConfig]
    dataset: DatasetConfig

    # Optional configurations with default values
    combinations_to_run: Optional[List[Tuple[str, Any]]] = None
    evaluators: Optional[List[Union[EvaluatorConfig,
                                    ComparisonEvaluatorConfig]]] = None
    output: Optional[OutputConfig] = None
    human_ratings: List[HumanRating] = field(default_factory=list)
    existing_experiment_path: Optional[str] = None
    version: Optional[str] = None
    output_parser: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


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


@dataclass
class Experiment:
    """
    Represents an entire experiment.

    Attributes:
    - results (List[ExperimentResult]): List of results for each input example.
    - aggregated_metrics (Dict[str, Dict[str, Metric]]): 
      A dictionary where keys are evaluator names and values are dictionaries mapping metric names to their values.
    - ... (other experiment attributes)
    """
    results: List[ExperimentResult]
    aggregated_metrics: Dict[str, Dict[str, Metric]]
