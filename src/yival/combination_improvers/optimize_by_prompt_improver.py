"""
This module provides an implementation of Large Language models as improvers, 
https://arxiv.org/pdf/2309.03409.pdf , which is /opro/ for short

The goal of this module is to improve and auto-generate the prompt with the 
ability of llms.

We construct the Prompt used to generate better prompt as follow:

***
HEAD_META_INSTRUCTION
SOLUTION_SCORE_PAIRS
OPTIMATION_TASK_FORMAT(optional)
END_META_INSTRUCTION
***

and after each iteration , the new propmt with evaluator score will be added to 
the SOLUTION_SCORE_PAIRS part.
"""

import json
from typing import Dict, List, Tuple

from ..common.model_utils import llm_completion
from ..experiment.evaluator import Evaluator
from ..experiment.utils import generate_experiment
from ..logger.token_logger import TokenLogger
from ..schemas.combination_improver_configs import (
    OptimizeByPromptImproverConfig,
)
from ..schemas.experiment_config import (
    Experiment,
    ExperimentConfig,
    ExperimentResult,
    ImproverOutput,
)
from ..schemas.model_configs import Request
from .base_combination_improver import BaseCombinationImprover

HEAD_META_INSTRUCTION = """
Now you will help me generate a prompt which is used to generate a corresponding
landing page headline according for a startup business named [tech_startup_business],
specializing in [business], and target_peopleing [target_people].
I already have some prompt and its evaluation results :
"""

END_META_INSTRUCTION = """
Give me a new prompt that is different from all pairs above, and has a evaluation
value higher than any of above. Do not write code. The prompt must be on the last line and start with "prompt:"
"""


def find_first_meta_data(experiment: Experiment) -> Tuple[Dict, Dict]:
    """
    Fine the best combination and its score from experiment. If the experiment
    has selection output , use the best combination from selection output.
    Otherwise , use the first combination from the experiment.
    """
    if experiment.selection_output:
        combo_string = experiment.selection_output.best_combination.replace(
            "'", "\""
        )
        best_combo = json.loads(combo_string)
        score = experiment.selection_output.selection_reason
        return best_combo, score
    else:
        #TODO add no selection output case
        return {}, {}


def construct_solution_score_pairs(cache: List[Tuple[Dict, Dict]]) -> str:
    """
    Construct the solution_score_pairs for the full prompt.
    This part will be longer after each iteration.
    To avoid the input is too long for llm , we will cut the cache to the
    latest five outputs
    """
    prompt = ""
    for prompt_dict, eval_dict in cache[-5:]:
        print(f"[DEBUG] prompt_dict:{prompt_dict}, eval_dict:{eval_dict}")
        prompt += 'Input:\n'
        #FIXME: support more variations than 'task'
        prompt += f"prompt: {prompt_dict.get('task','')}\n"
        prompt += 'Evaluation:\n'
        for evaluator_name, score in eval_dict.items():
            display = evaluator_name.split(":")[-1].strip()
            if display == "average_token_usage" or display == "average_latency":
                continue
            prompt += f"{display}: {score} "
        prompt += '\n'

    return prompt


def construct_opro_full_prompt(cache: List[Tuple[Dict, Dict]]) -> str:
    """
    Construct full opro prompt , which has a format as follow
    - HEAD_META_INSTRUCTION
    - SOLUTION_SCORE_PAIRS
    - OPTIMATION_TASK_FORMAT(optional)
    - END_META_INSTRUCTION
    """
    full_prompt = HEAD_META_INSTRUCTION + '\n' + construct_solution_score_pairs(
        cache
    ) + '\n' + END_META_INSTRUCTION
    return full_prompt


def fetch_next_prompt(prompt: str, model_name="gpt-4") -> str:
    """
    improve prompt according to opro improver
    fetch the next prompt from llm_completion
    """
    response = llm_completion(
        Request(
            model_name=model_name, prompt=prompt, params={"temperature": 0.3}
        )
    ).output

    llm_output_str = response["choices"][0]["message"]["content"]
    print(f"[DEBUG] llm output now :{response}\n output_str: {llm_output_str}")
    return llm_output_str


class OptimizeByPromptImprover(BaseCombinationImprover):
    """
    Optimization by PROmpting improver to improve and auto-generate combination.
    """
    default_config = OptimizeByPromptImproverConfig(
        name="optimize_by_prompt_improver",
        model_name="gpt-4",
        max_iterations=3
    )

    def __init__(self, config: OptimizeByPromptImproverConfig):
        super().__init__(config)
        self.config = config

    def improve(
        self, experiment: Experiment, config: ExperimentConfig,
        evaluator: Evaluator, token_logger: TokenLogger
    ) -> ImproverOutput:
        print(
            f"[INFO] into target optimizer\n evaluator:{evaluator} \n experiment:{experiment}"
        )
        experiments: List[Experiment] = []
        results: List[ExperimentResult] = []
        cache: List[Tuple[Dict, Dict]] = []
        original_combo_key = ""

        #init cache with the best combo
        best_combo, score = find_first_meta_data(experiment)
        cache.append((best_combo, score))
        print(f"best_combo: {best_combo} \n score:{score}")
        print(f"cache now is {cache}")

        first_prompt = construct_opro_full_prompt(cache)
        print(f"[DEBUG] first_prompt is now {first_prompt}")
        prompt_now = fetch_next_prompt(first_prompt, self.config.model_name)

        #optimize by prompt for max_iterations times
        for i in range(self.config.max_iterations + 1):
            print(f"[INFO][optimize_by_prompt_improver] start iteration{i}")

        experiment = generate_experiment(
            results, evaluator, evaluate_group=False, evaluate_all=False
        )

        improver_output = ImproverOutput(
            group_experiment_results=experiment.group_experiment_results,
            combination_aggregated_metrics=experiment.
            combination_aggregated_metrics,
            original_best_combo_key=original_combo_key
        )

        return improver_output


BaseCombinationImprover.register_combination_improver(
    "optimize_by_prompt_improver", OptimizeByPromptImprover,
    OptimizeByPromptImproverConfig
)