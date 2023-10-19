import copy
import string
from typing import Any, Dict, Iterable, List, Optional, Union

from ..schemas.evaluator_config import EvaluatorOutput, Rags_EvaluatorConfig
from ..schemas.experiment_config import ExperimentResult

from ragas import evaluate
from ragas.metrics import answer_relevancy,faithfulness
from datasets import Dataset
from ragas.metrics import answer_relevance,faithfulness
from .base_evaluator import BaseEvaluator


class RAGSEvaluator(BaseEvaluator):
    
    default_config = Rags_EvaluatorConfig(
        name="openai_prompt_based_evaluator"
    )

    def __init__(self,config:Rags_EvaluatorConfig):
        super().__init__(config)
        self.config=config

    def evaluate(self,experiment_result: ExperimentResult)-> EvaluatorOutput:
        format_dict = copy.deepcopy(experiment_result.input_data.content)
        format_dict['raw_output']=experiment_result.raw_output.text_output
        output,context=format_dict['raw_output'].split('\r')
        question=[format_dict['input']]
        answer=[output]
        context=[[context]]
        ds = Dataset.from_dict(
            {
                'question': question,
                'answer': answer,
                'context': context,
            }
        )
        metrics=[]
        metric_types=self.config.metric_type.split(',')
        if 'answer_relevancy' in metric_types:
            metrics.append(answer_relevancy)
        elif 'faithfulness' in metric_types:
            metrics.append(faithfulness)

        result=evaluate(ds, metrics=metrics)
        print(result)
        return EvaluatorOutput(
            name=self.config.name,
            result=result[metric_types[0]],
            display_name=metric_types[0],
            metric_calculators=self.config.metric_calculators
        )
BaseEvaluator.register_evaluator(
    "rags_evaluator", RAGSEvaluator,
    Rags_EvaluatorConfig
)