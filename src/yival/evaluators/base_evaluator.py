from abc import ABC, abstractmethod

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

    def __init__(self, config: BaseEvaluatorConfig):
        """
        Initialize the evaluator with its configuration.

        Args:
            config (BaseEvaluatorConfig): The configuration for the evaluator.

        """
        self.config = config

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
