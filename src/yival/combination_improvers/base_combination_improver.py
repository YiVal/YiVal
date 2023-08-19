from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type

from ..experiment.evaluator import Evaluator
from ..logger.token_logger import TokenLogger
from ..schemas.combination_improver_configs import (
    BaseCombinationImproverConfig,
)
from ..schemas.experiment_config import (
    Experiment,
    ExperimentConfig,
    ImproverOutput,
)


class BaseCombinationImprover(ABC):
    """
    Abstract base class for all combination improvers.
    
    Attributes:
        _registry (Dict[str, Dict[str, Any]]): A registry to keep track of combination improvers.
        default_config (Optional[BaseCombinationImproverConfig]): Default configuration for the combination improver.
    """

    _registry: Dict[str, Dict[str, Any]] = {}
    default_config: Optional[BaseCombinationImproverConfig] = None

    @classmethod
    def get_combination_improver(
        cls, name: str
    ) -> Optional[Type['BaseCombinationImprover']]:
        """Retrieve combination improver class from registry by its name."""
        return cls._registry.get(name, {}).get("class")

    @classmethod
    def get_default_config(
        cls, name: str
    ) -> Optional[BaseCombinationImproverConfig]:
        """Retrieve the default configuration of a combination improver by its name."""
        return cls._registry.get(name, {}).get("default_config")

    def __init__(self, config: BaseCombinationImproverConfig):
        self.config = config

    @classmethod
    def get_config_class(
        cls, name: str
    ) -> Optional[Type[BaseCombinationImproverConfig]]:
        """Retrieve the configuration class of a combination imporver by its name."""
        return cls._registry.get(name, {}).get("config_cls")

    @classmethod
    def register_combination_improver(
        cls,
        name: str,
        combination_improver_cls: Type['BaseCombinationImprover'],
        config_cls: Optional[Type[BaseCombinationImproverConfig]] = None
    ):
        """Register a new combination improver along with its default configuration and configuration class."""
        cls._registry[name] = {
            "class": combination_improver_cls,
            "default_config": combination_improver_cls.default_config,
            "config_cls": config_cls
        }

    @abstractmethod
    def improve(
        self, experiment: Experiment, config: ExperimentConfig,
        evaluator: Evaluator, token_logger: TokenLogger
    ) -> ImproverOutput:
        """
        Improve the experiment based on its results.

        Args:
            experiment (Experiment): The experiment with its results.
            config (ExperimentConfig): The original experiment configuration.
            evaluator (Evaluator): A utility class to evaluate the ExperimentResult.
            token_logger (TokenLogger): Logs the token usage.

        Returns:
            ImproverOutput
        """
        pass
