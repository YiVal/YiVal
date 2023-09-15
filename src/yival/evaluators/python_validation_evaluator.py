"""
Python Validation Evaluator Module.

This module provides an implementation of the PythonValidationEvaluator,
which evaluates the raw output of an experiment using Python's exec function.
The evaluator is designed to validate Python code snippets and determine
whether they can be executed without any errors.

Classes:
    - PythonValidationEvaluator: Evaluates the raw output of an experiment.
"""

from ..schemas.evaluator_config import (
    EvaluatorOutput,
    EvaluatorType,
    MatchingTechnique,
    MethodCalculationMethod,
    MetricCalculatorConfig,
    PythonValidationEvaluatorConfig,
)
from ..schemas.experiment_config import ExperimentResult
from .base_evaluator import BaseEvaluator


class PythonValidationEvaluator(BaseEvaluator):
    """
    Python Validation Evaluator.

    Evaluates the raw output of an experiment by attempting to execute it as
    Python code. If the code executes without any errors, a positive result is
    returned. Otherwise, a negative result is returned.
    """
    
    default_config = PythonValidationEvaluatorConfig(
        matching_technique=MatchingTechnique.MATCH,
        evaluator_type=EvaluatorType.INDIVIDUAL,
        name="python_validation_evaluator",
        metric_calculators=[
            MetricCalculatorConfig(
                MethodCalculationMethod(MethodCalculationMethod.AVERAGE)
            )
        ]
    )

    def __init__(self, config: PythonValidationEvaluatorConfig):

        super().__init__(config)
        self.config: PythonValidationEvaluatorConfig = config

    def evaluate(self, experiment_result: ExperimentResult) -> EvaluatorOutput:
        raw_output = experiment_result.raw_output
        res = 0
        try:
            exec(raw_output)
            res = 1
        except Exception:
            pass
    
        return EvaluatorOutput(
            name=self.config.name,
            display_name="matching",
            result=res,
            metric_calculators=self.config.metric_calculators
        )


BaseEvaluator.register_evaluator(
    "python_validation_evaluator", PythonValidationEvaluator,
    PythonValidationEvaluatorConfig
)
