"""
This module defines the base class for combination enhancers.

Combination enhancers are responsible for improving the combination of
experiments based on their experiment results.

"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type

from ..experiment.evaluator import Evaluator
from ..logger.token_logger import TokenLogger
from ..schemas.combination_enhancer_configs import BaseCombinationEnhancerConfig
from ..schemas.experiment_config import EnhancerOutput, Experiment, ExperimentConfig


class BaseCombinationEnhancer(ABC):
    """
    Abstract base class for all combination enhancers.
    Attributes:
        _registry (Dict[str, Dict[str, Any]]): A registry to keep track of
        combination enhancers.
        default_config (Optional[BaseCombinationenhancerConfig]): Default
        configuration for the combination enhancer.
    """

    _registry: Dict[str, Dict[str, Any]] = {}
    default_config: Optional[BaseCombinationEnhancerConfig] = None

    @classmethod
    def get_enhancer(cls,
                     name: str) -> Optional[Type['BaseCombinationEnhancer']]:
        """Retrieve combination enhancer class from registry by its name."""
        return cls._registry.get(name, {}).get("class")

    @classmethod
    def get_default_config(
        cls, name: str
    ) -> Optional[BaseCombinationEnhancerConfig]:
        """Retrieve the default configuration of a combination enhancer by its
           name."""
        return cls._registry.get(name, {}).get("default_config")

    def __init__(self, config: BaseCombinationEnhancerConfig):
        self.config = config

    @classmethod
    def get_config_class(
        cls, name: str
    ) -> Optional[Type[BaseCombinationEnhancerConfig]]:
        """Retrieve the configuration class of a combination imporver by its
           name."""
        return cls._registry.get(name, {}).get("config_cls")

    @classmethod
    def register_enhancer(
        cls,
        name: str,
        enhancer_cls: Type['BaseCombinationEnhancer'],
        config_cls: Optional[Type[BaseCombinationEnhancerConfig]] = None
    ):
        """Register a new combination enhancer along with its default
           configuration and configuration class."""
        cls._registry[name] = {
            "class": enhancer_cls,
            "default_config": enhancer_cls.default_config,
            "config_cls": config_cls
        }

    @abstractmethod
    def enhance(
        self, experiment: Experiment, config: ExperimentConfig,
        evaluator: Evaluator, token_logger: TokenLogger
    ) -> EnhancerOutput:
        """
        enhance the experiment based on its results.

        Args:
            experiment (Experiment): The experiment with its results.
            config (ExperimentConfig): The original experiment configuration.
            evaluator (Evaluator): A utility class to evaluate the
            ExperimentResult. token_logger (TokenLogger): Logs the token usage.

        Returns:
            enhancerOutput
        """
