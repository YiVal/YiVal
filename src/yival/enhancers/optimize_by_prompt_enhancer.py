"""
This module provides an implementation of Large Language models as enhancers, 
https://arxiv.org/pdf/2309.03409.pdf , which is /opro/ for short

The goal of this module is to enhance and auto-generate the prompt with the 
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

You can find an example in demo/configs/headline_generation_enhance.yml,
and more examples in paper appendix
"""

import copy
import json
import logging
from typing import Dict, List, Tuple

from ..common.model_utils import llm_completion
from ..experiment.evaluator import Evaluator
from ..experiment.lite_experiment import LiteExperimentRunner
from ..experiment.rate_limiter import RateLimiter
from ..experiment.utils import generate_experiment
from ..logger.token_logger import TokenLogger
from ..schemas.combination_enhancer_configs import OptimizeByPromptEnhancerConfig
from ..schemas.common_structures import InputData
from ..schemas.experiment_config import (
    EnhancerOutput,
    Experiment,
    ExperimentConfig,
    ExperimentResult,
)
from ..schemas.model_configs import Request
from .base_combination_enhancer import BaseCombinationEnhancer
from .utils import construct_output_format, format_input_from_dict, scratch_variations_from_str

rate_limiter = RateLimiter(60 / 60)


def find_combo_with_score(experiment: Experiment) -> Tuple[Dict, Dict]:
    """
    Fine the best combination and its score from experiment. If the experiment
    has selection output , use the best combination from selection output.
    Otherwise , use the first combination from the experiment.
    """
    best_combo = {}
    score = {}

    if experiment.selection_output:
        combo_string = experiment.selection_output.best_combination
        best_combo = json.loads(combo_string)  #type: ignore
        score = experiment.selection_output.selection_reason or {
        }  #type: ignore

    return best_combo, score


def find_origin_combo_key(experiment: Experiment) -> str:
    """
    Find the combo key from best_combination
    Ensure that we have selector config
    """
    if experiment.selection_output is not None:
        combo_key = experiment.selection_output.best_combination
        return combo_key
    else:
        raise ValueError("Selection output is None")


def construct_solution_score_pairs(
    cache: List[Tuple[Dict, Dict]], enhance_var: List[str]
) -> str:
    """
    Construct the solution_score_pairs for the full prompt.
    This part will be longer after each iteration.
    To avoid the input is too long for llm , we will cut the cache to the
    latest five outputs
    """
    prompt = ""
    for prompt_dict, eval_dict in cache[-5:]:
        prompt += 'Input:\n'
        prompt += format_input_from_dict(prompt_dict, enhance_var)
        prompt += 'Evaluation:\n'
        for evaluator_name, score in eval_dict.items():
            display = evaluator_name.split(":")[-1].strip()
            if display == "average_token_usage" or display == "average_latency":
                continue
            prompt += f"{display}: {score} "
        prompt += '\n'

    return prompt


def construct_opro_full_prompt(
    cache: List[Tuple[Dict, Dict]], head_meta_instruction: str,
    optimation_task_format: str | None, end_meta_instruction: str,
    enhance_var: List[str]
) -> str:
    """
    Construct full opro prompt , which has a format as follow
    - HEAD_META_INSTRUCTION
    - SOLUTION_SCORE_PAIRS
    - OPTIMATION_TASK_FORMAT(optional)
    - END_META_INSTRUCTION
    """

    full_prompt = head_meta_instruction + '\n'
    full_prompt += (construct_solution_score_pairs(cache, enhance_var) + '\n')
    if optimation_task_format:
        full_prompt += (optimation_task_format + '\n')
    full_prompt += (end_meta_instruction + '\n')
    full_prompt += construct_output_format(enhance_var)

    return full_prompt


def fetch_next_variations(prompt: str, model_name="gpt-4") -> str:
    """
    enhance prompt according to opro enhancer
    fetch the next variations from llm output
    """
    response = llm_completion(
        Request(
            model_name=model_name, prompt=prompt, params={"temperature": 1.0}
        )
    ).output

    llm_output_str = response["choices"][0]["message"]["content"].strip(
        "'"
    ).strip('"')
    return llm_output_str


def collect_all_data(experiment: Experiment) -> List[InputData]:
    datas: List[InputData] = []
    for r in experiment.combination_aggregated_metrics[0].experiment_results:
        input_data = copy.deepcopy(r.input_data)
        input_data.content.pop("raw_output", None)
        datas.append(input_data)
    return datas


class OptimizeByPromptEnhancer(BaseCombinationEnhancer):
    """
    Optimization by PROmpting enhancer to enhance and auto-generate combination.
    """

    default_config = OptimizeByPromptEnhancerConfig(
        name="optimize_by_prompt_enhancer",
        head_meta_instruction="",
        end_meta_instruction="",
        optimation_task_format="",
        enhance_var=["task"],
        model_name="gpt-4",
        max_iterations=3
    )

    def __init__(self, config: OptimizeByPromptEnhancerConfig):
        super().__init__(config)
        self.config: OptimizeByPromptEnhancerConfig = config

    def fetch_next_variations(self, prompt: str) -> Dict:
        """
        enhance variations according to opro
        
        make sure llm response format is valid and return new varations
        """
        response = llm_completion(
            Request(
                model_name=self.config.model_name,
                prompt=prompt,
                params={"temperature": 1.0}
            )
        ).output

        llm_output_str = response["choices"][0]["message"]["content"].strip(
            "'"
        ).strip('"')  #type: ignore

        variations = scratch_variations_from_str(
            llm_output_str, self.config.enhance_var
        )

        return variations

    def enhance(
        self, experiment: Experiment, config: ExperimentConfig,
        evaluator: Evaluator, token_logger: TokenLogger
    ) -> EnhancerOutput:
        experiments: List[Experiment] = []
        results: List[ExperimentResult] = []
        cache: List[Tuple[Dict, Dict]] = []
        original_combo_key = find_origin_combo_key(experiment)
        self.updated_config = copy.deepcopy(config)

        #init cache with the best combo
        best_combo, score = find_combo_with_score(experiment)

        #ensure that all variation in enhance_var appears best_combo
        assert set(self.config.enhance_var).issubset(set(best_combo.keys()))

        variations_now = best_combo
        logging.info(f"[INFO][opro] first variations is {variations_now}")

        lite_experiment_runner = LiteExperimentRunner(
            config=self.updated_config,
            limiter=rate_limiter,
            data=collect_all_data(experiment),
            token_logger=token_logger,
            evaluator=evaluator
        )

        #optimize by prompt for max_iterations times
        for i in range(self.config.max_iterations + 1):
            logging.info(
                f"[INFO][optimize_by_prompt_enhancer] start iteration [{i}]"
            )

            #update variations and run experiment
            lite_experiment_runner.set_variations([{
                key: [value]
                for key, value in variations_now.items()
            }])

            experiment = lite_experiment_runner.run_experiment(
                enable_selector=True
            )
            experiments.append(experiment)

            #fetch next prompt
            best_combo, score = find_combo_with_score(experiment)
            cache.append((best_combo, score))

            opro_prompt = construct_opro_full_prompt(
                cache, self.config.head_meta_instruction,
                self.config.optimation_task_format,
                self.config.end_meta_instruction, self.config.enhance_var
            )

            gen_variations = self.fetch_next_variations(opro_prompt)

            if not gen_variations:
                logging.info(
                    f"[INFO][optimize_by_prompt_enhancer] fetch next variations error"
                )
            else:
                logging.info(
                    f"[INFO][optimize_by_prompt_enhancer] generate new variations: {gen_variations}"
                )
                variations_now = gen_variations

        for exp in experiments:
            for res in exp.combination_aggregated_metrics:
                results.extend(res.experiment_results)

        experiment = generate_experiment(
            results, evaluator, evaluate_group=False, evaluate_all=False
        )

        enhancer_output = EnhancerOutput(
            group_experiment_results=experiment.group_experiment_results,
            combination_aggregated_metrics=experiment.
            combination_aggregated_metrics,
            original_best_combo_key=original_combo_key
        )

        return enhancer_output


BaseCombinationEnhancer.register_enhancer(
    "optimize_by_prompt_enhancer", OptimizeByPromptEnhancer,
    OptimizeByPromptEnhancerConfig
)