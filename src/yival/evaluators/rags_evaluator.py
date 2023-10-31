import copy
import string
from typing import Any, Dict, Iterable, List, Optional, Union

from ..schemas.evaluator_config import EvaluatorOutput, Rags_EvaluatorConfig
from ..schemas.experiment_config import ExperimentResult

from ragas import evaluate # type: ignore
from ragas.metrics import answer_relevancy,faithfulness,context_precision # type: ignore
from datasets import Dataset # type: ignore
from .base_evaluator import BaseEvaluator
import numpy as np
from yival.wrappers.string_wrapper import StringWrapper

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
        question=[format_dict['question']]
        answer=[output]
        contexts=[context.split('---')]
        ds = Dataset.from_dict(
            {
                'question': question,
                'answer': answer,
                'contexts': contexts,
            }
        )
        metrics=[]
        metric_types=self.config.metric_type.split(',')
        if 'answer_relevancy' in metric_types:
            metrics.append(answer_relevancy)
        if 'faithfulness' in metric_types:
            metrics.append(faithfulness)
        if 'context_precision' in metric_types:
            metrics.append(context_precision)
        result=evaluate(ds, metrics=metrics)
        f_res=np.array([result[metric] for metric in metric_types])
        return EvaluatorOutput(
            name=self.config.name,
            result=f_res,
            display_name=str(metric_types),
            metric_calculators=self.config.metric_calculators
        )
BaseEvaluator.register_evaluator(
    "rags_evaluator", RAGSEvaluator,
    Rags_EvaluatorConfig
)