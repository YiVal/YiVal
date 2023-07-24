from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, List, Optional


@dataclass
class MetricCalculatorConfig:
    """
    Configuration for metric calculation.

    Attributes:
    - method (str): Method or algorithm used for calculation.
    - ... (any other configuration parameters for metric calculation)
    """
    method: str


class EvaluatorType(Enum):
    INDIVIDUAL = "individual"
    COMPARISON = "comparison"
    # Additional evaluator types can be added here as needed.


class MatchingTechnique(Enum):
    FUZZY_MATCH = "fuzzy_match"
    JSON_VALIDATOR = "json_validator"
    MATCH = "match"


@dataclass
class BaseEvaluatorConfig:
    """
    Base configuration for evaluators.
    """
    name: str
    evaluator_type: EvaluatorType


@dataclass
class EvaluatorConfig(BaseEvaluatorConfig):
    """
    Configuration for custom evaluator.
    """

    custom_function: Optional[Callable] = None
    metric_calculators: List[MetricCalculatorConfig] = field(
        default_factory=list
    )


@dataclass
class ComparisonEvaluatorConfig(BaseEvaluatorConfig):
    """
    Configuration for evaluators that compare different outputs.
    """

    comparison_function: Callable
    metric_calculators: List[MetricCalculatorConfig] = field(
        default_factory=list
    )


@dataclass
class ExpectedResultEvaluatorConfig(BaseEvaluatorConfig):
    matching_technique: MatchingTechnique


@dataclass
class EvaluatorOutput:
    """
    Result of an evaluator.

    Attributes:
    - name (str): Name of the evaluator.
    - result (Any): Result produced by the evaluator.
    """

    name: str
    result: Any
