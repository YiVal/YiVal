# test_string_expected_result_evaluator.py

from ..schemas.common_structures import InputData
from ..schemas.evaluator_config import (
    EvaluatorType,
    ExpectedResultEvaluatorConfig,
    MatchingTechnique,
)
from .string_expected_result_evaluator import StringExpectedResultEvaluator


def test_string_expected_result_evaluator_fuzzy_match():
    # Test with fuzzy matching technique
    config = ExpectedResultEvaluatorConfig(
        name="Fuzzy Match",
        matching_technique=MatchingTechnique.FUZZY_MATCH,
        evaluator_type=EvaluatorType.INDIVIDUAL
    )
    evaluator = StringExpectedResultEvaluator(config)
    input_data = InputData(
        content="Hello world!", expected_result="hello world", example_id="id"
    )  # Fuzzy match should be True
    result = evaluator.evaluate(input_data, raw_output="Hello world!")
    assert result.result == 1


def test_string_expected_result_evaluator_json_validator():
    # Test with JSON validation technique
    config = ExpectedResultEvaluatorConfig(
        name="JSON Validator",
        matching_technique=MatchingTechnique.JSON_VALIDATOR,
        evaluator_type=EvaluatorType.INDIVIDUAL
    )
    evaluator = StringExpectedResultEvaluator(config)
    input_data = InputData(
        content='{"name": "John", "age": 30}',
        expected_result='',
        example_id="id"
    )  # Empty expected_result, always True
    result = evaluator.evaluate(
        input_data, raw_output='{"name": "John", "age": 30}'
    )
    assert result.result == 1


def test_string_expected_result_evaluator_exact_match():
    # Test with exact matching technique
    config = ExpectedResultEvaluatorConfig(
        name="Exact Match",
        matching_technique=MatchingTechnique.MATCH,
        evaluator_type=EvaluatorType.INDIVIDUAL
    )
    evaluator = StringExpectedResultEvaluator(config)
    input_data = InputData(
        content="Hello world!",
        expected_result="Hello world!",
        example_id="id"
    )  # Exact match should be True
    result = evaluator.evaluate(input_data, raw_output="Hello world!")
    assert result.result == 1


def test_string_expected_result_evaluator_exact_match_failure():
    # Test with exact matching technique and failure case
    config = ExpectedResultEvaluatorConfig(
        name="Exact Match",
        matching_technique=MatchingTechnique.MATCH,
        evaluator_type=EvaluatorType.INDIVIDUAL
    )
    evaluator = StringExpectedResultEvaluator(config)
    input_data = InputData(
        content="Hello world!",
        expected_result="Goodbye world!",
        example_id="id"
    )  # Exact match should be False
    result = evaluator.evaluate(input_data, raw_output="Hello world!")
    assert result.result == 0


def test_string_expected_result_evaluator_invalid_json():
    # Test with JSON validation technique and invalid JSON
    config = ExpectedResultEvaluatorConfig(
        name="JSON Validator",
        matching_technique=MatchingTechnique.JSON_VALIDATOR,
        evaluator_type=EvaluatorType.INDIVIDUAL
    )
    evaluator = StringExpectedResultEvaluator(config)
    input_data = InputData(
        content='{"name": "John", "age": 30',
        expected_result='',
        example_id="id"
    )  # Invalid JSON, should be False
    result = evaluator.evaluate(
        input_data, raw_output='{"name": "John", "age": 30'
    )
    assert result.result == 0
