from dataclasses import dataclass
from typing import Dict, List, Optional


# Configurations
@dataclass
class BaseConfig:
    pass  # Common configuration attributes for all selection methods


@dataclass
class AHPConfig(BaseConfig):
    criteria: List[str]
    criteria_weights: Dict[str, float]
    criteria_maximization: Dict[str, bool]
    normalize_func: Optional[str] = None


@dataclass
class SelectionOutput:
    best_combination: str
    selection_reason: Optional[Dict[str, float]] = None
