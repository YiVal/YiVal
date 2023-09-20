# test_string_expected_result_evaluator.py
import pytest

from yival.evaluators.string_expected_result_evaluator import (
    StringExpectedResultEvaluator,
)
from yival.schemas.common_structures import InputData
from yival.schemas.evaluator_config import (
    EvaluatorType,
    ExpectedResultEvaluatorConfig,
    MatchingTechnique,
)
from yival.schemas.experiment_config import (
    EvaluatorOutput,
    ExperimentResult,
    MultimodalOutput,
)


@pytest.fixture
def evaluator():
    config = ExpectedResultEvaluatorConfig(
        matching_technique=MatchingTechnique.INCLUDES,
        evaluator_type=EvaluatorType.INDIVIDUAL,
        name="string_expected_result",
        metric_calculators=[]
    )
    return StringExpectedResultEvaluator(config)


def test_evaluate_includes_matching(evaluator):
    # Mock data
    input_data = InputData(
        content={"abc": "def"}, expected_result="hello world"
    )
    experiment_result = ExperimentResult(
        input_data=input_data,
        combination={},
        raw_output=MultimodalOutput(text_output="hello world"),
        latency=0.1,
        token_usage=5
    )
    expected_output = EvaluatorOutput(
        name=evaluator.config.name,
        result=1,
        metric_calculators=evaluator.config.metric_calculators
    )

    # Run the evaluator
    output = evaluator.evaluate(experiment_result)

    # Assert the output
    assert output.name == expected_output.name
    assert output.result == expected_output.result
    assert output.metric_calculators == expected_output.metric_calculators
