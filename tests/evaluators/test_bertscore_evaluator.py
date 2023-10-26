from unittest.mock import MagicMock, patch

from yival.evaluators.bertscore_evaluator import (
    BertScoreEvaluator,
    BertScoreEvaluatorConfig,
    ExperimentResult,
    InputData,
    MultimodalOutput,
)


def test_bert_score_evaluator_init():
    config = BertScoreEvaluatorConfig(name="bertscore_evaluator")
    evaluator = BertScoreEvaluator(config)

    assert isinstance(evaluator, BertScoreEvaluator)
    assert evaluator.config == config


@patch('yival.evaluators.bertscore_evaluator.score')
def test_bert_score_evaluator_evaluate(mocked_score):
    # Mock the score function to return fixed values
    mocked_score.return_value = (
        MagicMock(item=MagicMock(return_value=0.8)),
        MagicMock(item=MagicMock(return_value=0.9)),
        MagicMock(item=MagicMock(return_value=0.95))
    )

    config = BertScoreEvaluatorConfig(
        name="bertscore_evaluator", indicator="p"
    )
    evaluator = BertScoreEvaluator(config)

    input_data_example = InputData(
        content={
            "instruction": "translate the sentence to english",
        },
        expected_result="Have a great day!"
    )
    experiment_result_example = ExperimentResult(
        input_data=input_data_example,
        combination={
            "wrapper1": "var1",
            "wrapper2": "var2"
        },
        raw_output=MultimodalOutput(text_output="have a nice day"),
        latency=30.0,
        token_usage=20
    )

    result = evaluator.evaluate(experiment_result_example)

    assert result.result == 0.8

    # Test for another indicator
    config = BertScoreEvaluatorConfig(
        name="bertscore_evaluator", indicator="f"
    )
    evaluator = BertScoreEvaluator(config)
    result = evaluator.evaluate(experiment_result_example)

    assert result.result == 0.95
