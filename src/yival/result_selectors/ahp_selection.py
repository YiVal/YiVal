from typing import Any, Dict

import numpy as np

from ..schemas.experiment_config import (
    CombinationAggregatedMetrics,
    EvaluatorOutput,
    Experiment,
)
from ..schemas.selector_strategies import AHPConfig, SelectionOutput
from .normalize_func import NORMALIZATION_FUNCS
from .selection_context import SelectionContext
from .selection_strategy import SelectionStrategy


class AHPSelection(SelectionStrategy):
    config: AHPConfig
    default_config: AHPConfig = AHPConfig(
        criteria=["average_token_usage", "average_latency"],
        criteria_weights={
            "average_token_usage": 0.5,
            "average_latency": 0.5
        },
        criteria_maximization={
            "average_token_usage": False,
            "average_latency": False
        },
        normalize_func=None,
    )

    def __init__(self, config: AHPConfig):
        super().__init__(config)
        self.config = config

    def select(self, experiment: Experiment) -> SelectionOutput:
        scores = {}
        combination_data = {}
        alternatives_data = []

        print(f"[INFO] experiment:{experiment}")

        # Convert each combination's metrics to a criteria vector
        for combo in experiment.combination_aggregated_metrics:
            data = self._extract_data(combo)
            alternatives_data.append(self._get_criteria_vector(data))
            combination_data[combo.combo_key] = data

        # Create a matrix of alternatives data
        matrix: np.ndarray = np.array(alternatives_data)

        # Normalize matrix data
        if self.config.normalize_func:
            matrix = NORMALIZATION_FUNCS[self.config.normalize_func](matrix)

        # Apply criteria weights
        weights = np.array([
            self.config.criteria_weights[criterion]
            for criterion in self.config.criteria
        ])
        weighted_matrix = matrix * weights

        # If the criterion should be minimized, invert the corresponding
        # column in the matrix
        for i, criterion in enumerate(self.config.criteria):
            if not self.config.criteria_maximization.get(criterion, True):
                weighted_matrix[:, i] *= -1

        # Aggregate the scores
        aggregate_scores = np.sum(weighted_matrix, axis=1)

        # Extract combinations and their aggregate scores
        for i, combo in enumerate(experiment.combination_aggregated_metrics):
            scores[combo.combo_key] = aggregate_scores[i]

        # Select the combination with the highest aggregate score
        best_combination = max(scores, key=lambda k: scores[k])

        # Calculate the contribution of each criterion to the final score
        # based on the original data and weights
        contributions = {
            criterion:
            self.config.criteria_weights[criterion] *
            combination_data[best_combination].get(criterion, 0)
            for criterion in self.config.criteria
        }

        # Adjust the contribution for minimization criteria
        for criterion, value in contributions.items():
            if not self.config.criteria_maximization.get(criterion, True):
                contributions[criterion] = -value

        return SelectionOutput(
            best_combination=best_combination, selection_reason=contributions
        )

    def _get_criteria_vector(self, data: Dict[str, float]) -> np.ndarray:
        """Converts data dictionary into a vector based on the criteria order
        in config."""
        return np.array([
            data.get(criterion, 0) for criterion in self.config.criteria
        ])

    def _extract_data(self,
                      combo: CombinationAggregatedMetrics) -> Dict[str, Any]:
        data = {}

        if "average_token_usage" in self.config.criteria:
            data["average_token_usage"] = combo.average_token_usage or 0
        if "average_latency" in self.config.criteria:
            data["average_latency"] = combo.average_latency or 0

        # Extract data from evaluator_outputs
        for evaluator_output in (combo.combine_evaluator_outputs or []):
            if evaluator_output.name in self.config.criteria:
                data[evaluator_output.name] = evaluator_output.result

        for metric_name, metric_values in combo.aggregated_metrics.items():
            if metric_name in self.config.criteria:
                data[metric_name] = sum([
                    metric.value for metric in metric_values
                ]) / len(metric_values)
        return data


SelectionStrategy.register_strategy("ahp_selection", AHPSelection, AHPConfig)


def main():
    combination_A = CombinationAggregatedMetrics(
        combo_key=str({"name": "A"}),
        experiment_results=[],
        aggregated_metrics={},
        average_token_usage=120,
        average_latency=200,
        combine_evaluator_outputs=[EvaluatorOutput(name="elo", result=1500)]
    )

    # Combination B has a lower elo, but also much lower token usage and
    # latency
    combination_B = CombinationAggregatedMetrics(
        combo_key=str({"name": "B"}),
        experiment_results=[],
        aggregated_metrics={},
        average_token_usage=50,
        average_latency=50,
        combine_evaluator_outputs=[EvaluatorOutput(name="elo", result=1300)]
    )

    #Combination C has highest elo with highest token usage and latency
    combination_C = CombinationAggregatedMetrics(
        combo_key=str({"name": "C"}),
        experiment_results=[],
        aggregated_metrics={},
        average_token_usage=300,
        average_latency=300,
        combine_evaluator_outputs=[EvaluatorOutput(name="elo", result=1600)]
    )

    # The experiment data
    trade_off_test_data = Experiment(
        combination_aggregated_metrics=[
            combination_A, combination_B, combination_C
        ],
        group_experiment_results=[]
    )

    config_trade_off = AHPConfig(
        criteria=["elo", "average_token_usage", "average_latency"],
        criteria_weights={
            "elo": 0.6,
            "average_token_usage": 0.2,
            "average_latency": 0.2
        },
        criteria_maximization={
            "elo": True,
            "average_token_usage": False,
            "average_latency": False
        },
        normalize_func='z-score'
    )
    context_trade_off = SelectionContext(
        strategy=AHPSelection(config=config_trade_off)
    )
    best_combo_trade_off = context_trade_off.execute_selection(
        trade_off_test_data
    )
    print(best_combo_trade_off)


if __name__ == "__main__":
    main()
