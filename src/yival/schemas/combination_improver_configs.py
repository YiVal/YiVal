from dataclasses import asdict, dataclass
from typing import Dict, Optional

from .selector_strategies import SelectionOutput


@dataclass
class BaseCombinationImproverConfig:
    """
    Base configuration class for all combination improvers.
    """
    pass

    def asdict(self):
        return asdict(self)


@dataclass
class OpenAIPromptBasedCombinationImproverConfig(
    BaseCombinationImproverConfig
):
    name = "openai_prompt_based_combination_improver"
    openai_model_name: str = "gpt-4"
    max_iterations: int = 3
    stop_conditions: Optional[Dict[str, float]] = None
    average_score: Optional[float] = None
    selection_strategy: Optional[SelectionOutput] = None

    def asdict(self):
        return asdict(self)
