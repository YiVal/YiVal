"""
BERTScore is a metric for evaluating text generation models by calculating the 
similarity of two sentences in the BERT embedding space.
"""

import copy

from yival.schemas.evaluator_config import BaseEvaluatorConfig

from ..schemas.evaluator_config import (
    BertScoreEvaluatorConfig,
    EvaluatorOutput,
)
from ..schemas.experiment_config import ExperimentResult
from .base_evaluator import BaseEvaluator


class BertScoreEvaluator(BaseEvaluator):
    """Evaluator using bert_score evaluation"""

    default_config = BertScoreEvaluatorConfig(name="bertsocre_evaluator")

    def __init__(self, config: BaseEvaluatorConfig):
        super().__init__(config)
        self.config = config

    def evaluate(self, experiment_result: ExperimentResult) -> EvaluatorOutput:
        """Evaluate the experiment result according to bert score"""
        assert isinstance(self.config, BertScoreEvaluatorConfig)

        cans = copy.deepcopy(experiment_result.input_data.content)
        ref = copy.deepcopy(experiment_result.input_data.expected_result)

        assert ref is not None
