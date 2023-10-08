import json
from typing import Dict, List

from datasets import Dataset as HgDataset
from transformers import AutoTokenizer, PreTrainedTokenizer, PreTrainedTokenizerFast

from ..dataset.data_utils import evaluate_condition

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

    if experiment.enable_custom_func:
        for combo_result in experiment.combination_aggregated_metrics:
            print(f"combo_result now : {combo_result}")
            results: List[ExperimentResult] = combo_result.experiment_results
            for rs in results:
                if rs.evaluator_outputs:
                    for evaluator_output in rs.evaluator_outputs:
                        condition_met = evaluate_condition(
                            condition, evaluator_output
                        )
                        print(f"conditiom_met now : {condition_met}")
                        if condition_met:
                            prompt = rs.input_data['content'][prompt_key]
                            completion = rs.input_data['content'][
                                completion_key
                            ] if completion_key else rs.input_data[
                                'expected_result']
                            result_dict['prompt'].append(prompt)
                            result_dict['completion'].append(completion)

    else:
        for rs in experiment.group_experiment_results:
            input_data = json.loads(rs.group_key)
            prompt = input_data['content'][prompt_key]
            completion = input_data['content'][
                completion_key] if completion_key else input_data[
                    'expected_result']

            result_dict['prompt'].append(prompt)
            result_dict['completion'].append(completion)

    hg_dataset = HgDataset.from_dict(result_dict)
    return hg_dataset
