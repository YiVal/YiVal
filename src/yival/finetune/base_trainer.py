"""
This module defines the base class for trainer

Trainers are responsible for finetune llms locally based on 
the data and experiment results
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type

from ..experiment.evaluator import Evaluator
from ..logger.token_logger import TokenLogger
from ..schemas.experiment_config import (
    Experiment,
    ExperimentConfig,
    TrainerOutput,
)
from ..schemas.trainer_configs import BaseTrainerConfig


class BaseTrainer(ABC):
    """
    Abstract base class for all trainers
    Attributes:
        _register (Dict[str, Dict[str,Any]]): A register to keep track of 
        trainers
        default_config (Optional[BaseTrainerConfig]): Default configuration
        for the trainers
    """

    _registry: Dict[str, Dict[str, Any]] = {}
    default_config: Optional[BaseTrainerConfig] = None

    @classmethod
    def get_trainer(cls, name: str) -> Optional[Type['BaseTrainer']]:
        """Retrieve trainer class from registry by its name."""
        return cls._registry.get(name, {}).get("class")

    @classmethod
    def get_default_config(cls, name: str) -> Optional[BaseTrainerConfig]:
        """Retrieve the default configuration of a trainer from the name"""
        return cls._registry.get(name, {}).get("default_config")

    def __init__(self, config: BaseTrainerConfig) -> None:
        self.config = config

    @classmethod
    def get_config_class(cls, name: str) -> Optional[Type[BaseTrainerConfig]]:
        return cls._registry.get(name, {}).get("config_cls")

    @classmethod
    def register_trainer(
        cls,
        name: str,
        trainer_cls: Type['BaseTrainer'],
        config_cls: Optional[Type[BaseTrainerConfig]] = None
    ):
        """Register a new trainer along with its defualt configuration
           and configuration class."""
        cls._registry[name] = {
            "class": trainer_cls,
            "defualt_config": trainer_cls.default_config,
            "config_cls": config_cls
        }

    @abstractmethod
    def train(
        self, experiment: Experiment, config: ExperimentConfig,
        evaluator: Evaluator, token_logger: TokenLogger
    ) -> TrainerOutput:
        """
        Train models based on the configs and datas

        Args:
            experiment (Experiment): The experiment with its results.
            config (ExperimentConfig): The original experiment configuration.
            evaluator (Evaluator): A utility class to evaluate the
            ExperimentResult. token_logger (TokenLogger): Logs the token usage.
        
        Returns:
            TrainerOutput
        """
