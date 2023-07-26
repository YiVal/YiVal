from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type

from ..schemas.common_structures import InputData
from ..schemas.evaluator_config import BaseEvaluatorConfig, EvaluatorOutput


class BaseEvaluator(ABC):
    """
    Base class for all evaluators.

    This class provides the basic structure and methods for evaluators.
    Specific evaluators should inherit from this class and implement the necessary methods.

    Attributes:
        config (BaseEvaluatorConfig): The configuration for the evaluator.

    """
    _registry: Dict[str, Dict[str, Any]] = {}
    default_config: Optional[BaseEvaluatorConfig] = None

    def __init__(self, config: BaseEvaluatorConfig):
        """
        Initialize the evaluator with its configuration.

        Args:
            config (BaseEvaluatorConfig): The configuration for the evaluator.

        """
        self.config = config

    @classmethod
    def register(cls, name: str):
        """Decorator to register new evaluators."""

        def inner(subclass: Type[BaseEvaluator]):
            cls._registry[name] = {
                "class": subclass,
                "default_config": subclass.default_config
            }
            return subclass

        return inner

    @classmethod
    def get_evaluator(cls, name: str) -> Optional[Type['BaseEvaluator']]:
        """Retrieve evaluator class from registry by its name."""
        evaluator_info = cls._registry.get(name, {})
        return evaluator_info.get(
            "class", None
        ) if "class" in evaluator_info else None

    @classmethod
    def get_default_config(cls, name: str) -> Optional[BaseEvaluatorConfig]:
        """Retrieve the default configuration of an evaluator by its name."""
        evaluator_info = cls._registry.get(name, {})
        return evaluator_info.get(
            "default_config", None
        ) if "default_config" in evaluator_info else None

    @abstractmethod
    def evaluate(
        self, input_data: InputData, raw_output: str
    ) -> EvaluatorOutput:
        """
        Evaluate the input data and produce an evaluator output.

        Args:
            input_data (InputData): The input data to be evaluated.
            raw_output (str): The raw output produced by the custom function.

        Returns:
            EvaluatorOutput: The result of the evaluation.

        """
        pass
