import json

from datasets import Dataset as HgDataset
from transformers import (
    AutoTokenizer,
    PreTrainedTokenizer,
    PreTrainedTokenizerFast,
)

from ..schemas.experiment_config import Experiment


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
    experiment: Experiment, prompt_key: str, completion_key: str | None
) -> HgDataset:
    result_dict = {"prompt": [], "completion": []}
    for rs in experiment.group_experiment_results:
        input_data = json.loads(rs.group_key)
        prompt = input_data['content'][prompt_key]
        completion = input_data['content'][
            completion_key] if completion_key else input_data['expected_result']

        result_dict['prompt'].append(prompt)
        result_dict['completion'].append(completion)

    hg_dataset = HgDataset.from_dict(result_dict)
    return hg_dataset
