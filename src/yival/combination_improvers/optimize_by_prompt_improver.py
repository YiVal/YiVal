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

import copy
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Tuple

from tqdm import tqdm

from ..common.model_utils import llm_completion
from ..experiment.evaluator import Evaluator
from ..experiment.rate_limiter import RateLimiter
from ..experiment.utils import (
    generate_experiment,
    get_selection_strategy,
    run_single_input,
)
from ..logger.token_logger import TokenLogger
from ..result_selectors.selection_context import SelectionContext
from ..schemas.combination_improver_configs import (
    OptimizeByPromptImproverConfig,
)
from ..schemas.common_structures import InputData
from ..schemas.experiment_config import (
    Experiment,
    ExperimentConfig,
    ExperimentResult,
    ImproverOutput,
    WrapperConfig,
    WrapperVariation,
)
from ..schemas.model_configs import Request
from ..states.experiment_state import ExperimentState
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

OPTIMATION_TASK_FORMAT = """
"""

rate_limiter = RateLimiter(10 / 60)


def find_first_meta_data(experiment: Experiment) -> Tuple[Dict, Dict]:
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


def construct_solution_score_pairs(cache: List[Tuple[Dict, Dict]]) -> str:
    """
    Construct the solution_score_pairs for the full prompt.
    This part will be longer after each iteration.
    To avoid the input is too long for llm , we will cut the cache to the
    latest five outputs
    """
    prompt = ""
    for prompt_dict, eval_dict in cache[-5:]:
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

    def parallel_task(self, data, all_combinations, logger, evaluator):
        """
        Execute a single input run in parallel
        """
        rate_limiter()
        return run_single_input(
            data,
            self.updated_config,
            all_combinations=all_combinations,
            logger=logger,
            evaluator=evaluator
        )

    def improve(
        self, experiment: Experiment, config: ExperimentConfig,
        evaluator: Evaluator, token_logger: TokenLogger
    ) -> ImproverOutput:
        assert isinstance(self.config, OptimizeByPromptImproverConfig)
        experiments: List[Experiment] = []
        results: List[ExperimentResult] = []
        cache: List[Tuple[Dict, Dict]] = []
        original_combo_key = find_origin_combo_key(experiment)
        self.updated_config = copy.deepcopy(config)

        #init cache with the best combo
        best_combo, score = find_first_meta_data(experiment)
        cache.append((best_combo, score))

        prompt_now = best_combo["task"]
        logging.info(f"[INFO][opro] first prompt now is {prompt_now}")

        #optimize by prompt for max_iterations times
        for i in range(self.config.max_iterations + 1):
            logging.info(
                f"[INFO][optimize_by_prompt_improver] start iteration{i}"
            )
            current_iteration_results: List[ExperimentResult] = []

            #FIXME: supporm more variations other than 'task'
            self.updated_config.variations = []
            self.updated_config["variations"].append(( #type: ignore
                WrapperConfig(
                    name="task",
                    variations=[
                        WrapperVariation(
                            value=prompt_now,
                            value_type=str(type(prompt_now)).split("'")[1]
                        )
                    ]
                )
            ))

            state = ExperimentState.get_instance()
            state.clear_variations_for_experiment()
            state.set_experiment_config(self.updated_config)
            state.active = True
            all_combinations = state.get_all_variation_combinations()
            data = collect_all_data(experiment)
            total = len(data)

            with tqdm(
                total=total, desc="[opro_improver]Processing", unit="item"
            ) as pbar:
                with ThreadPoolExecutor() as executor:
                    for res in executor.map(
                        self.parallel_task, data,
                        [all_combinations] * len(data),
                        [token_logger] * len(data), [evaluator] * len(data)
                    ):
                        current_iteration_results.extend(res)
                        pbar.update(len(res))

            experiment = generate_experiment(
                current_iteration_results,
                evaluator,
                evaluate_group=False,
                evaluate_all=False
            )

            strategy = get_selection_strategy(self.updated_config)
            if strategy:
                context_trade_off = SelectionContext(strategy=strategy)
                experiment.selection_output = context_trade_off.execute_selection( # type: ignore
                    experiment=experiment
                )
            experiments.append(experiment)

            best_combo, score = find_first_meta_data(experiment)
            cache.append((best_combo, score))

            opro_prompt = construct_opro_full_prompt(cache)
            prompt_now = fetch_next_prompt(opro_prompt, self.config.model_name)

        for exp in experiments:
            for res in exp.combination_aggregated_metrics:
                results.extend(res.experiment_results)

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