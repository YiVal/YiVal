"""
Selection Strategy Module.

This module defines an abstract base class for selection strategies.
A selection strategy 
determines how to select or prioritize specific experiments, scenarios, or
configurations based on certain criteria.

"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type

from ..schemas.experiment_config import Experiment
from ..schemas.selector_strategies import BaseConfig, SelectionOutput


class SelectionStrategy(ABC):
    """
    Abstract base class for selection strategies.
    """
    _registry: Dict[str, Dict[str, Any]] = {}
    default_config: Optional[BaseConfig] = None

    @abstractmethod
    def select(self, experiment: Experiment) -> SelectionOutput:
        pass

    @classmethod
    def register_strategy(
        cls,
        name: str,
        strategy_cls: Type['SelectionStrategy'],
        config_cls: Optional[Type[BaseConfig]] = None
    ):
        cls._registry[name] = {
            "class": strategy_cls,
            "default_config": strategy_cls.default_config,
            "config_cls": config_cls
        }

    @classmethod
    def get_strategy(cls, name: str) -> Optional[Type['SelectionStrategy']]:
        """Retrieve strategy class from registry by its name."""
        strategy_info = cls._registry.get(name, {})
        return strategy_info.get(
            "class", None
        ) if "class" in strategy_info else None

    @classmethod
    def get_default_config(cls, name: str) -> Optional[BaseConfig]:
        """Retrieve the default configuration of a strategy by its name."""
        strategy_info = cls._registry.get(name, {})
        return strategy_info.get(
            "default_config", None
        ) if "default_config" in strategy_info else None

    @classmethod
    def get_config_class(cls, name: str) -> Optional[Type[BaseConfig]]:
        strategy_info = cls._registry.get(name, {})
        return strategy_info.get("config_cls", None)

    def __init__(self, config: BaseConfig):
        self.config = config
