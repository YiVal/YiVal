import pytest

from yival.result_selectors.ahp_selection import (
    AHPConfig,
    AHPSelection,
    CombinationAggregatedMetrics,
    Experiment,
)
from yival.schemas.experiment_config import EvaluatorOutput


@pytest.fixture
def basic_experiment():
    return Experiment(
        combination_aggregated_metrics=[
            CombinationAggregatedMetrics(
                combo_key="combo1",
                average_token_usage=50,
                average_latency=100,
                experiment_results=[],
                aggregated_metrics={}
            ),
            CombinationAggregatedMetrics(
                combo_key="combo2",
                average_token_usage=30,
                average_latency=200,
                experiment_results=[],
                aggregated_metrics={}
            ),
        ],
        group_experiment_results=[
        ]  # Default value for simplicity; adjust as needed
    )


@pytest.fixture
def ahp_selection():
    config = AHPConfig(
        criteria=["average_token_usage", "average_latency", "custom_metric"],
        criteria_weights={
            "average_token_usage": 0.7,
            "average_latency": 0.3,
            "custom_metric": 0.5
        },
        criteria_maximization={
            "average_token_usage": True,
            "average_latency": False,
            "custom_metric": True
        }
    )
    return AHPSelection(config)


def test_ahp_selection(basic_experiment, ahp_selection):
    result = ahp_selection.select(basic_experiment)
    assert result.best_combination == "combo1"
    assert result.selection_reason["average_token_usage"] == 50 * 0.7
    assert result.selection_reason[
        "average_latency"
    ] == -100 * 0.3  # Negative because it's a minimization criterion


def test_criteria_vector(ahp_selection):
    data = {"average_token_usage": 50, "average_latency": 100}
    vector = ahp_selection._get_criteria_vector(data)
    assert vector[0] == 50
    assert vector[1] == 100


def test_extract_data(ahp_selection):
    combo = CombinationAggregatedMetrics(
        combo_key="combo1",
        average_token_usage=50,
        average_latency=100,
        combine_evaluator_outputs=[
            EvaluatorOutput(name="custom_metric", result=150)
        ],
        experiment_results=[],
        aggregated_metrics={}
    )
    data = ahp_selection._extract_data(combo)
    assert data["average_token_usage"] == 50
    assert data["average_latency"] == 100
    assert data["custom_metric"] == 150
