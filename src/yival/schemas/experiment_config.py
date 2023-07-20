"""
Module for experiment configuration structures.

This module provides data structures to capture configurations required to run an
experiment.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union


@dataclass
class WrapperConfig:
    """
    Configuration for each individual wrapper used in the experiment.

    Attributes:
    - name (str): Name of the wrapper.
    - variations (List[Any]): List of variations for this wrapper.
    - ground_truth (Optional[Callable]): Optional ground truth function or data for
      this wrapper.
    """

    name: str
    variations: List[Any]
    ground_truth: Optional[Callable] = None


class InputType(Enum):
    """
    Enum to specify the type of input: directly from the user or from a dataset.
    """

    USER = "user_input"
    DATASET = "dataset"


@dataclass
class DatasetConfig:
    """
    Configuration for the dataset used in the experiment.

    Attributes:
    - input_type (InputType): Type of input, either directly from the user or from a
      dataset.
    - file_path (Union[str, None]): Path to the dataset file. Relevant only if
      input_type is DATASET.
    - reader (Union[Callable, None]): Callable to read and process the dataset file.
      Relevant only if input_type is DATASET.
    """

    input_type: InputType
    file_path: Union[str, None] = None
    reader: Union[Callable, None] = None


@dataclass
class EvaluatorConfig:
    """
    Configuration for custom evaluator.

    Attributes:
    - evaluator_type (str): Type of evaluator (individual, comparison, etc.).
    - custom_function (Optional[Callable]): Custom evaluator function if any.
    """

    evaluator_type: str
    custom_function: Optional[Callable] = None


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
class ExperimentConfig:
    """
    Consolidated configuration for running an experiment.

    Attributes:
    - description (str): Description of the experiment.
    - wrappers (List[WrapperConfig]): List of wrapper configurations.
    - dataset (DatasetConfig): Dataset configuration.
    - evaluator (EvaluatorConfig): Evaluator configuration.
    - output (OutputConfig): Output configuration.
    - existing_experiment_path (Optional[str]): Path to an existing experiment for
      incremental experiments or comparisons.
    - version (Optional[str]): Version or timestamp for the experiment.
    - metadata (Dict[str, Any]): Additional metadata related to the experiment.
    """

    description: str
    wrappers: List[WrapperConfig]
    dataset: DatasetConfig
    evaluator: EvaluatorConfig
    output: OutputConfig
    existing_experiment_path: Optional[str] = None
    version: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
