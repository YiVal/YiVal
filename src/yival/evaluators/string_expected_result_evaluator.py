"""
Module: string_expected_result_evaluator.py

This module defines the StringExpectedResultEvaluator class, which is used for
evaluating string expected results.

Classes:
    StringExpectedResultEvaluator: Class for evaluating string expected
    results.

"""

import json
from typing import List, Union
from PIL.PngImagePlugin import PngImageFile

from ..schemas.evaluator_config import (
    EvaluatorOutput,
    EvaluatorType,
    ExpectedResultEvaluatorConfig,
    MatchingTechnique,
    MethodCalculationMethod,
    MetricCalculatorConfig,
)
from ..schemas.experiment_config import ExperimentResult
from .base_evaluator import BaseEvaluator
from .utils import fuzzy_match_util


def is_valid_json(s: Union[str, List[PngImageFile]]) -> bool:
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
        config (ExpectedResultEvaluatorConfig): Configuration object for the
                                                evaluator.

    """
    default_config = ExpectedResultEvaluatorConfig(
        matching_technique=MatchingTechnique.INCLUDES,
        evaluator_type=EvaluatorType.INDIVIDUAL,
        name="string_expected_result",
        metric_calculators=[
            MetricCalculatorConfig(
                MethodCalculationMethod(MethodCalculationMethod.AVERAGE)
            )
        ]
    )

    def __init__(self, config: ExpectedResultEvaluatorConfig):
        """
        Initialize the StringExpectedResultEvaluator with the provided
        configuration.

        Args:
            config (ExpectedResultEvaluatorConfig): Configuration object for
            the evaluator.

        """
        super().__init__(config)
        self.config: ExpectedResultEvaluatorConfig = config

    def evaluate(self, experiment_result: ExperimentResult) -> EvaluatorOutput:
        """
        Evaluate the expected result against the actual result using the
        specified matching technique.

        Returns:
            EvaluatorOutput: An EvaluatorOutput object containing the
            evaluation result.

        """
        input_data = experiment_result.input_data
        raw_output = experiment_result.raw_output
        expected_result = input_data.expected_result
        is_match = False
        technique = MatchingTechnique(self.config.matching_technique)
        if technique == MatchingTechnique.FUZZY_MATCH:
            if not expected_result:
                is_match = True
            else:
                is_match = fuzzy_match_util(raw_output, expected_result)
        elif technique == MatchingTechnique.JSON_VALIDATOR:
            is_match = is_valid_json(raw_output)
        elif technique == MatchingTechnique.MATCH:
            if not expected_result:
                is_match = True
            else:
                is_match = expected_result == raw_output
        elif technique == MatchingTechnique.INCLUDES:
            if not expected_result:
                is_match = True
            else:
                is_match = expected_result in raw_output

        result = 1 if is_match else 0
        return EvaluatorOutput(
            name=self.config.name,
            display_name="matching",
            result=result,
            metric_calculators=self.config.metric_calculators
        )


BaseEvaluator.register_evaluator(
    "string_expected_result", StringExpectedResultEvaluator,
    ExpectedResultEvaluatorConfig
)
