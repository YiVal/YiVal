from dataclasses import asdict, dataclass
from typing import Dict, List, Optional

from .selector_strategies import SelectionOutput


@dataclass
class BaseCombinationEnhancerConfig:
    """
    Base configuration class for all combination enhancers.
    """
    name: str

    def asdict(self):
        return asdict(self)


@dataclass
class OpenAIPromptBasedCombinationEnhancerConfig(
    BaseCombinationEnhancerConfig
):
    openai_model_name: str = "gpt-4"
    max_iterations: int = 3
    stop_conditions: Optional[Dict[str, float]] = None
    average_score: Optional[float] = None
    selection_strategy: Optional[SelectionOutput] = None

    def asdict(self):
        return asdict(self)


@dataclass
class OptimizeByPromptEnhancerConfig(BaseCombinationEnhancerConfig):
    enhance_var: List[str]
    head_meta_instruction: str
    end_meta_instruction: str
    optimation_task_format: Optional[str] = None
    model_name: str = "gpt-4"
    max_iterations: int = 3


@dataclass
class PE2EnhancerConfig(BaseCombinationEnhancerConfig):
    enhance_var: List[str]
    enable_prompt_instruction: bool
    full_prompt_description: str
    max_iterations: int = 3
    batch_size: int = 3
    step_size: Optional[int] = None
    max_token: Optional[int] = 200