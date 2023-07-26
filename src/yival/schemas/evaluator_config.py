from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, List


class MethodCalculationMethod(Enum):
    """
    Configuration for metric calculation method.

    """
    AVERAGE = "average"


@dataclass
class MetricCalculatorConfig:
    """
    Configuration for metric calculation.
    """
    method: MethodCalculationMethod

    def asdict(self):
        return asdict(self)


class MatchingTechnique(Enum):
    FUZZY_MATCH = "fuzzy_match"
    JSON_VALIDATOR = "json_validator"
    INCLUDES = "includes"
    MATCH = "match"

    def __str__(self):
        return self.value


class EvaluatorType(Enum):
    INDIVIDUAL = "individual"
    COMPARISON = "comparison"

    def __str__(self):
        return self.value


@dataclass
class BaseEvaluatorConfig:
    """
    Base configuration for evaluators.
    """
    name: str
    evaluator_type: EvaluatorType

    def asdict(self):
        result = asdict(self)
        result["evaluator_type"] = self.evaluator_type.name
        return result


@dataclass
class EvaluatorConfig(BaseEvaluatorConfig):
    """
    Configuration for custom evaluator.
    """
    metric_calculators: List[MetricCalculatorConfig] = field(
        default_factory=list
    )
    evaluator_type = EvaluatorType.INDIVIDUAL


@dataclass
class ComparisonEvaluatorConfig(BaseEvaluatorConfig):
    """
    Configuration for evaluators that compare different outputs.
    """
    metric_calculators: List[MetricCalculatorConfig] = field(
        default_factory=list
    )
    evaluator_type = EvaluatorType.COMPARISON


@dataclass
class ExpectedResultEvaluatorConfig(EvaluatorConfig):
    matching_technique: MatchingTechnique = MatchingTechnique.MATCH


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

    def asdict(self):
        return asdict(self)
