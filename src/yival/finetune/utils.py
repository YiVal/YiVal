import json
from typing import Dict, List

import pandas as pd
from datasets import Dataset as HgDataset  # type: ignore
from transformers import AutoTokenizer, PreTrainedTokenizer, PreTrainedTokenizerFast

from ..dataset.data_utils import (
    evaluate_condition,
    read_code_from_path_or_module,
    transform_experiment_result_generic,
)
from ..schemas.experiment_config import Experiment, ExperimentResult


def get_hg_tokenizer(
    model_name: str
) -> (PreTrainedTokenizer | PreTrainedTokenizerFast):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    return tokenizer


def print_trainable_parameters(model):
    """
    Prints the number of trainable parameters in the model.
    """
    trainable_params = 0
    all_param = 0
    for _, param in model.named_parameters():
        all_param += param.numel()
        if param.requires_grad:
            trainable_params += param.numel()
    print(
        f"trainable params: {trainable_params} || all params: {all_param} || trainables%: {100 * trainable_params / all_param}"
    )


def extract_from_input_data(
    experiment: Experiment, prompt_key: str, completion_key: str | None,
    condition: str | None
) -> HgDataset:
    """
    if experiment doesn't support custom_func , extract all data from group_experiment_results

    else extract data from combination_aggregated_metrics according to condition

    An example of condition: 'name == openai_prompt_based_evaluator AND result >= 0 AND display_name == clarity'

    """
    result_dict: Dict = {"prompt": [], "completion": []}

    if experiment.enable_custom_func and condition:
        code = read_code_from_path_or_module(
            "demo.headline_generation_detail.headline_generation"
        )
        if not code:
            print("[Error][utils] code load error")
            exit()
        else:
            for combo_result in experiment.combination_aggregated_metrics:
                results: List[ExperimentResult
                              ] = combo_result.experiment_results
                for rs in results:
                    if rs.evaluator_outputs:
                        for evaluator_output in rs.evaluator_outputs:
                            condition_met = evaluate_condition(
                                condition, evaluator_output
                            )
                            if not condition_met:
                                continue
                            result_pair = transform_experiment_result_generic(
                                code, rs
                            )
                            result_dict['prompt'].append(result_pair['Input'])
                            result_dict['completion'].append(
                                result_pair['Output']
                            )
    else:
        for group_rs in experiment.group_experiment_results:
            input_data = json.loads(group_rs.group_key)  #type: ignore
            prompt = input_data['content'][prompt_key]
            completion = input_data['content'][
                completion_key] if completion_key else input_data[
                    'expected_result']

            result_dict['prompt'].append(prompt)
            result_dict['completion'].append(completion)
    hg_dataset = HgDataset.from_dict(result_dict)
    return hg_dataset


def display_dataset(dataset: HgDataset, n_items: int = 5):
    n_items = min(n_items, len(dataset) - 1)
    data_slice = [dataset[i] for i in range(n_items)]
    df = pd.DataFrame(data_slice)
    print(df)