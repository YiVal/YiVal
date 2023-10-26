from typing import List

from alpaca_eval.annotators import PairwiseAnnotator

from yival.evaluators.base_evaluator import BaseEvaluator
from yival.schemas.evaluator_config import AlpacaEvalEvaluatorConfig, EvaluatorType
from yival.schemas.experiment_config import EvaluatorOutput, ExperimentResult


class AlpacaEvalEvaluator(BaseEvaluator):

    config: AlpacaEvalEvaluatorConfig
    default_config: AlpacaEvalEvaluatorConfig

    def __init__(self, config: AlpacaEvalEvaluatorConfig):
        super().__init__(config)
        self.config: AlpacaEvalEvaluatorConfig = config

    def evaluate_comparison(self, group_data: List[ExperimentResult]) -> None:
        if len(group_data) < 2:
            raise ValueError(
                "Expected at least two ExperimentResults for comparison."
            )

        annotator = PairwiseAnnotator(
            annotators_config=self.config.alpaca_annotator_name
        )

        # Prepare lists for bulk annotation
        outputs_1 = []
        outputs_2 = []

        for i, result_i in enumerate(group_data):
            for j, result_j in enumerate(group_data[i + 1:], start=i + 1):
                outputs_1.append({
                    "instruction":
                    str(result_i.input_data.content),
                    "output":
                    result_i.raw_output.text_output
                })
                outputs_2.append({
                    "instruction":
                    str(result_j.input_data.content),
                    "output":
                    result_j.raw_output.text_output
                })

        # Bulk annotate
        annotations = annotator.annotate_head2head(
            outputs_1=outputs_1,
            outputs_2=outputs_2,
            keys_to_merge=["instruction"],
            is_ordered=True
        )

        # Scoring based on annotations
        scores: dict[int, float] = {i: 0 for i in range(len(group_data))}

        annotation_idx = 0
        for i, _ in enumerate(group_data):
            for j, _ in enumerate(group_data[i + 1:], start=i + 1):
                preference = annotations[annotation_idx]['preference']
                if preference == 1:
                    scores[i] += 1
                elif preference == 2:
                    scores[j] += 1

                annotation_idx += 1

        max_score = max(scores.values())
        min_score = min(scores.values())

        for key in scores:
            scores[key] = (scores[key] - min_score) / (max_score - min_score)

        for i, experiment_result in enumerate(group_data):
            evaluator_output = EvaluatorOutput(
                name="alpaca_evaluator",
                display_name=self.config.alpaca_annotator_name,
                result=scores[i],
                metric_calculators=self.config.metric_calculators
            )
            if experiment_result.evaluator_outputs:
                experiment_result.evaluator_outputs.append(evaluator_output)
            else:
                experiment_result.evaluator_outputs = [evaluator_output]


BaseEvaluator.register_evaluator(
    "alpaca_eval_evaluator", AlpacaEvalEvaluator, AlpacaEvalEvaluatorConfig
)


def main():
    from yival.schemas.experiment_config import InputData, MultimodalOutput
    sample_group_data = [
        ExperimentResult(
            input_data=InputData(
                content={"question": "How do I reset my password?"}
            ),
            combination={"model": "A"},
            raw_output=MultimodalOutput(
                text_output="Go to settings and click on 'Reset Password'."
            ),
            latency=2.5,
            token_usage=50
        ),
        ExperimentResult(
            input_data=InputData(
                content={"question": "How do I reset my password?"}
            ),
            combination={"model": "B"},
            raw_output=MultimodalOutput(
                text_output=
                "Navigate to 'Account', then select 'Change Password'."
            ),
            latency=2.7,
            token_usage=52
        ),
        ExperimentResult(
            input_data=InputData(
                content={"question": "How do I reset my password?"}
            ),
            combination={"model": "C"},
            raw_output=MultimodalOutput(
                text_output="As an AI model, I don't know how to do that."
            ),
            latency=2.7,
            token_usage=52
        ),
    ]
    evaluator_config = AlpacaEvalEvaluatorConfig(
        name="alpaca_eval_evaluator",
        alpaca_annotator_name="alpaca_eval_gpt4",
        evaluator_type=EvaluatorType.COMPARISON
    )
    evaluator = AlpacaEvalEvaluator(evaluator_config)
    evaluator.evaluate_comparison(sample_group_data)
    for experiment in sample_group_data:
        print(experiment.evaluator_outputs)


if __name__ == "__main__":
    main()
