from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class MethodCalculationMethod(Enum):
    """
    Configuration for metric calculation method.

    """
    AVERAGE = "AVERAGE"

    def __str__(self):
        return self.value


@dataclass
class MetricCalculatorConfig:
    """
    Configuration for metric calculation.
    """
    method: MethodCalculationMethod

    def asdict(self) -> Dict[str, Any]:
        return {"method": str(self.method)}


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
    ALL = "all"

    def __str__(self):
        return self.value


@dataclass
class BaseEvaluatorConfig:
    """
    Base configuration for evaluators.
    """
    name: str
    evaluator_type: EvaluatorType
    display_name: Optional[str] = None

    def asdict(self) -> Dict[str, Any]:
        return {"name": self.name, "evaluator_type": str(self.evaluator_type)}


@dataclass
class EvaluatorConfig(BaseEvaluatorConfig):
    """
    Configuration for custom evaluator.
    """
    metric_calculators: List[MetricCalculatorConfig] = field(
        default_factory=list
    )
    evaluator_type = EvaluatorType.INDIVIDUAL

    def asdict(self) -> Dict[str, Any]:
        base_dict = super().asdict()
        mcs = []
        for mc in self.metric_calculators:
            if isinstance(mc, MetricCalculatorConfig):
                mcs.append(mc.asdict())
            else:
                mcs.append(mc)
        base_dict["metric_calculators"] = mcs
        return base_dict


@dataclass
class ComparisonEvaluatorConfig(BaseEvaluatorConfig):
    """
    Configuration for evaluators that compare different outputs.
    """
    metric_calculators: List[MetricCalculatorConfig] = field(
        default_factory=list
    )
    evaluator_type = EvaluatorType.COMPARISON

    def asdict(self) -> Dict[str, Any]:
        base_dict = super().asdict()
        base_dict["metric_calculators"] = [
            mc.asdict() for mc in self.metric_calculators
        ]
        return base_dict


@dataclass
class GlobalEvaluatorConfig(BaseEvaluatorConfig):
    """
    Configuration for evaluators that compare based on all outputs.
    """
    metric_calculators: List[MetricCalculatorConfig] = field(
        default_factory=list
    )
    evaluator_type = EvaluatorType.ALL


@dataclass
class ExpectedResultEvaluatorConfig(EvaluatorConfig):
    matching_technique: MatchingTechnique = MatchingTechnique.MATCH


@dataclass
class PythonValidationEvaluatorConfig(EvaluatorConfig):
    matching_technique: MatchingTechnique = MatchingTechnique.MATCH


@dataclass
class AlpacaEvalEvaluatorConfig(ComparisonEvaluatorConfig):
    alpaca_annotator_name: str = "alpaca_eval_gpt4"
    matching_technique: MatchingTechnique = MatchingTechnique.MATCH


@dataclass
class OpenAIEloEvaluatorConfig(GlobalEvaluatorConfig):
    openai_model_name: str = "gpt-4"
    input_description: str = "This is a description."


@dataclass
class EvaluatorOutput:
    """
    Result of an evaluator.
    """

    name: str
    result: Any
    display_name: Optional[str] = None
    metric_calculators: List[MetricCalculatorConfig] = field(
        default_factory=list
    )

    def asdict(self) -> Dict[str, Any]:
        return {
            "name":
            self.name,
            "result":
            self.result,
            "display_name":
            self.display_name if self.display_name else self.name,
            "metric_calculators": [
                mc.asdict() if hasattr(mc, 'asdict') else mc
                for mc in self.metric_calculators
            ]
        }


@dataclass
class OpenAIPromptBasedEvaluatorConfig(EvaluatorConfig):
    evaluator_type: EvaluatorType = EvaluatorType.INDIVIDUAL
    prompt: Union[str, List[Dict[str, str]]] = ""
    choices: List[str] = field(default_factory=list)
    model_name: str = "gpt-4"
    description: str = "This is the description of the evaluator."
    scale_description: str = "0-4"
    choice_scores: Optional[Dict[str, float]] = None

    def asdict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RougeEvaluatorConfig(EvaluatorConfig):
    evaluator_type: EvaluatorType = EvaluatorType.INDIVIDUAL
    description: str = " This is the description of the evaluator"
    rough_type: str = "rouge-1"


@dataclass
class BertScoreEvaluatorConfig(EvaluatorConfig):
    evaluator_type: EvaluatorType = EvaluatorType.INDIVIDUAL
    description: str = " This is the description of the evaluator"
    lan: str = 'zh'
    indicator: str = 'p'  # p,r,f
