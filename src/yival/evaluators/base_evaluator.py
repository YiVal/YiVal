"""
Evaluators Module.

This module contains the base class and common methods for evaluators used in
experiments.
Evaluators are essential components in the system that interpret the results
of experiments and provide quantitative or qualitative feedback. Specific
evaluators are expected to inherit from the base class and implement custom
evaluation logic as needed.

"""
from abc import ABC
from typing import Any, Dict, List, Optional, Type, TypeVar

from ..schemas.evaluator_config import BaseEvaluatorConfig, EvaluatorOutput
from ..schemas.experiment_config import Experiment, ExperimentResult

T_Evaluator = TypeVar("T_Evaluator", bound="BaseEvaluator")


class BaseEvaluator(ABC):
    """
    Base class for all evaluators.

    This class provides the basic structure and methods for evaluators.
    Specific evaluators should inherit from this class and implement the
    necessary methods.

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

    @classmethod
    def register_evaluator(
        cls,
        name: str,
        reader_cls: Type[T_Evaluator],
        config_cls: Optional[Type[BaseEvaluatorConfig]] = None
    ):
        cls._registry[name] = {
            "class": reader_cls,
            "default_config": reader_cls.default_config,
            "config_cls": config_cls
        }

    @classmethod
    def get_config_class(cls,
                         name: str) -> Optional[Type[BaseEvaluatorConfig]]:
        """Retrieve the configuration class of a reader by its name."""
        reader_info = cls._registry.get(name, {})
        return reader_info.get("config_cls", None)

    def evaluate(self, experiment_result: ExperimentResult) -> EvaluatorOutput:
        """
        Evaluate the experiment result and produce an evaluator output.

        Args:
            experiment_result (ExperimentResult): The result of an experiment
            to be evaluated.

        Returns:
            EvaluatorOutput: The result of the evaluation.
        """
        return EvaluatorOutput("evaluate", "evaluate")

    async def aevaluate(self, experiment_result: ExperimentResult) -> Any:
        """
        Evaluate the experiment result and produce an evaluator output.

        Args:
            experiment_result (ExperimentResult): The result of an experiment
            to be evaluated.

        Returns:
            EvaluatorOutput: The result of the evaluation.
        """
        return EvaluatorOutput("evaluate", "evaluate")

    def evaluate_comparison(self, group_data: List[ExperimentResult]) -> None:
        """
        Evaluate and compare a list of experiment results.

        This method is designed to evaluate multiple experiment results
        together, allowing for comparisons and potentially identifying trends,
        anomalies, or other patterns in the set of results.

        Args:
            group_data (List[ExperimentResult]): A list of experiment results
            to be evaluated together.

        Note:
            Implementations of this method in subclasses should handle the
            specifics of how multiple experiments are evaluated and compared.
        """

    def evaluate_based_on_all_results(
        self, experiment: List[Experiment]
    ) -> None:
        """
        Evaluate based on the entirety of experiment results.
        
        This method evaluates an entire list of experiments, potentially taking 
        into account all available data to produce a comprehensive evaluation.
        
        Args:
            experiment (List[Experiment]): A list of all experiments to be
            evaluated.

        Note:
            Implementations of this method in subclasses should determine how
            to best utilize all available experiment data for evaluation.
        """
