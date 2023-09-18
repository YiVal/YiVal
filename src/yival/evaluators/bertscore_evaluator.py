"""
BERTScore is a language model evaluation metric based on the BERT language model. 
It leverages the pre-trained contextual embeddings from BERT and matches words in candidate and reference sentences by cosine similarity. 
It has been shown to correlate with human judgment on sentence-level and system-level evaluation.
"""

from bert_score import score  # type:ignore

from ..schemas.common_structures import InputData
from ..schemas.evaluator_config import (
    BertScoreEvaluatorConfig,
    EvaluatorOutput,
)
from ..schemas.experiment_config import ExperimentResult, MultimodalOutput
from .base_evaluator import BaseEvaluator


class BertScoreEvaluator(BaseEvaluator):
    """Evaluator calculate bert_score"""
    default_config = BertScoreEvaluatorConfig(name="bertsocre_evaluator")

    def __init__(self, config: BertScoreEvaluatorConfig):
        super().__init__(config)
        self.config = config

    def evaluate(self, experiment_result: ExperimentResult) -> EvaluatorOutput:
        """Evaluate the experiment result according to bertsocre"""
        assert isinstance(self.config, BertScoreEvaluatorConfig)
        input_data = experiment_result.input_data
        raw_output = experiment_result.raw_output.text_output
        expected_result = input_data.expected_result

        p, r, f1 = score([raw_output], [expected_result],
                         lang=self.config.lan,
                         verbose=True)

        scores = {"p": p.item(), "r": r.item(), "f": f1.item()}
        result = scores.get(self.config.indicator, .0)

        return EvaluatorOutput(
            name=self.config.name,
            display_name=self.config.display_name,
            result=result,
            metric_calculators=self.config.metric_calculators
        )


BaseEvaluator.register_evaluator(
    "bertscore_evaluator", BertScoreEvaluator, BertScoreEvaluatorConfig
)


def main():
    """Main function to test the bertscore evaluator"""
    evaluator_config = BertScoreEvaluatorConfig(
        name="bertscore_evaluator",
        display_name="rouge",
        metric_calculators=[],
    )
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

    evaluator = BertScoreEvaluator(evaluator_config)
    result = evaluator.evaluate(experiment_result_example)
    print(result)


if __name__ == "__main__":
    main()