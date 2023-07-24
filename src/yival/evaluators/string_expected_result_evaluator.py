"""
Module: string_expected_result_evaluator.py

This module defines the StringExpectedResultEvaluator class, which is used for evaluating string expected results.

Classes:
    StringExpectedResultEvaluator: Class for evaluating string expected results.

"""

import json

from ..schemas.common_structures import InputData
from ..schemas.evaluator_config import (
    EvaluatorOutput,
    ExpectedResultEvaluatorConfig,
    MatchingTechnique,
)
from .base_evaluator import BaseEvaluator
from .utils import fuzzy_match_util


def is_valid_json(s: str) -> bool:
    """
    Check if the given string is a valid JSON.

    Args:
        s (str): The input string to check.

    Returns:
        bool: True if the input string is a valid JSON, False otherwise.

    """

    try:
        json.loads(s)
        return True
    except ValueError:
        return False


class StringExpectedResultEvaluator(BaseEvaluator):
    """
    Class for evaluating string expected results.

    This class extends the BaseEvaluator and provides specific implementation
    for evaluating string expected results using different matching techniques.

    Attributes:
        config (ExpectedResultEvaluatorConfig): Configuration object for the evaluator.

    """

    def __init__(self, config: ExpectedResultEvaluatorConfig):
        """
        Initialize the StringExpectedResultEvaluator with the provided configuration.

        Args:
            config (ExpectedResultEvaluatorConfig): Configuration object for the evaluator.

        """
        super().__init__(config)
        self.config: ExpectedResultEvaluatorConfig = config

    def evaluate(
        self, input_data: InputData, raw_output: str
    ) -> EvaluatorOutput:
        """
        Evaluate the expected result against the actual result using the specified matching technique.

        Args:
            input_data (InputData): Input data containing the actual result and expected result.
            raw_output (str): The raw output produced by the custom function.

        Returns:
            EvaluatorOutput: An EvaluatorOutput object containing the evaluation result.

        """
        expected_result = input_data.expected_result

        is_match = False
        if self.config.matching_technique == MatchingTechnique.FUZZY_MATCH:
            if not expected_result:
                is_match = True
            else:
                is_match = fuzzy_match_util(raw_output, expected_result)
        elif self.config.matching_technique == MatchingTechnique.JSON_VALIDATOR:
            is_match = is_valid_json(raw_output)
        elif self.config.matching_technique == MatchingTechnique.MATCH:
            if not expected_result:
                is_match = True
            else:
                is_match = expected_result == raw_output

        result = 1 if is_match else 0
        return EvaluatorOutput(name=self.config.name, result=result)
