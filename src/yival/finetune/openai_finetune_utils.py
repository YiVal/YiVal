import json
import os
import pickle
import time
from collections import defaultdict
from typing import Dict, List

import numpy as np
import openai
import tiktoken
from openai import OpenAI

from yival.dataset.data_utils import (
    evaluate_condition,
    read_code_from_path_or_module,
    transform_experiment_result_generic,
)
from yival.schemas.experiment_config import Experiment, ExperimentResult

encoding = tiktoken.get_encoding("cl100k_base")

TARGET_EPOCHS = 3
MIN_TARGET_EXAMPLES = 100
MAX_TARGET_EXAMPLES = 25000
MIN_DEFAULT_EPOCHS = 1
MAX_DEFAULT_EPOCHS = 25


def num_tokens_from_messages(
    messages, tokens_per_message=3, tokens_per_name=1
):
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3
    return num_tokens


def num_assistant_tokens_from_messages(messages):
    num_tokens = 0
    for message in messages:
        if message["role"] == "assistant":
            num_tokens += len(encoding.encode(message["content"]))
    return num_tokens


def _print_distribution(values, name):
    print(f"\n#### Distribution of {name}:")
    print(f"min / max: {min(values)}, {max(values)}")
    print(f"mean / median: {np.mean(values)}, {np.median(values)}")
    print(f"p5 / p95: {np.quantile(values, 0.1)}, {np.quantile(values, 0.9)}")


def _print_stats(dataset: list[dict[str, list[dict[str, str]]]]):
    n_missing_system = 0
    n_missing_user = 0
    n_messages = []
    convo_lens = []
    assistant_message_lens = []
    MAX_TOKENS_PER_EXAMPLE = 4096

    for ex in dataset:
        messages = ex["messages"]
        if not any(message["role"] == "system" for message in messages):
            n_missing_system += 1
        if not any(message["role"] == "user" for message in messages):
            n_missing_user += 1
        n_messages.append(len(messages))
        convo_lens.append(num_tokens_from_messages(messages))
        assistant_message_lens.append(
            num_assistant_tokens_from_messages(messages)
        )

    print("Num examples missing system message:", n_missing_system)
    print("Num examples missing user message:", n_missing_user)
    _print_distribution(n_messages, "num_messages_per_example")
    _print_distribution(convo_lens, "num_total_tokens_per_example")
    _print_distribution(
        assistant_message_lens, "num_assistant_tokens_per_example"
    )
    n_too_long = sum(l > 4096 for l in convo_lens)
    print(
        f"\n{n_too_long} examples may be over the 4096 token limit, they will be truncated during fine-tuning"
    )

    n_epochs = TARGET_EPOCHS
    n_train_examples = len(dataset)
    if n_train_examples * TARGET_EPOCHS < MIN_TARGET_EXAMPLES:
        n_epochs = min(
            MAX_DEFAULT_EPOCHS, MIN_TARGET_EXAMPLES // n_train_examples
        )
    elif n_train_examples * TARGET_EPOCHS > MAX_TARGET_EXAMPLES:
        n_epochs = max(
            MIN_DEFAULT_EPOCHS, MAX_TARGET_EXAMPLES // n_train_examples
        )

    n_billing_tokens_in_dataset = sum(
        min(MAX_TOKENS_PER_EXAMPLE, length) for length in convo_lens
    )
    print(
        f"Dataset has ~{n_billing_tokens_in_dataset} tokens that will be charged for during training"
    )
    print(f"By default, you'll train for {n_epochs} epochs on this dataset")
    print(
        f"By default, you'll be charged for ~{n_epochs * n_billing_tokens_in_dataset} tokens"
    )


def validate_message(dataset) -> bool:
    # Format error checks
    format_errors: dict[str, int] = defaultdict(int)

    for ex in dataset:
        if not isinstance(ex, dict):
            format_errors["data_type"] += 1
            continue

        messages = ex.get("messages", None)
        if not messages:
            format_errors["missing_messages_list"] += 1
            continue

        for message in messages:
            if "role" not in message or "content" not in message:
                format_errors["message_missing_key"] += 1

            if any(k not in ("role", "content", "name") for k in message):
                format_errors["message_unrecognized_key"] += 1

            if message.get("role",
                           None) not in ("system", "user", "assistant"):
                format_errors["unrecognized_role"] += 1

            content = message.get("content", None)
            if not content or not isinstance(content, str):
                format_errors["missing_content"] += 1

        if not any(
            message.get("role", None) == "assistant" for message in messages
        ):
            format_errors["example_missing_assistant_message"] += 1

    if format_errors:
        print("Found errors:")
        for k, v in format_errors.items():
            print(f"{k}: {v}")
        return False
    else:
        print("No errors found")
        return True


def _format_data_for_chatgpt_finetune(
    data: List[Dict[str, str]],
    system_prompt: str = "",
) -> List[Dict[str, List[Dict[str, str]]]]:
    """
    Transforms the input data to the desired data for finetune.

    Args:
    - system_prompt (str): System message to include at the start of each chat.
    - data (List[Dict[str, str]]): List of data points with 'Input' and 'Output' keys.

    Returns:
    - List[Dict[str, List[Dict[str, str]]]]: Formatted data.
    """
    formatted_data = []

    for entry in data:
        chat_entry: dict[str, list[dict[str, str]]] = {"messages": []}
        if system_prompt:
            chat_entry["messages"].append({
                "role": "system",
                "content": system_prompt
            })
        elif "Instruction" in entry:
            chat_entry["messages"].append({
                "role": "system",
                "content": entry["Instruction"]
            })
        chat_entry["messages"].append({
            "role": "user",
            "content": entry["Input"]
        })
        chat_entry["messages"].append({
            "role": "assistant",
            "content": entry["Output"]
        })
        formatted_data.append(chat_entry)

    return formatted_data


def finetune(
    input_file: str,
    condition: str,
    custom_function: str,
    system_prompt: str = "",
    model_suffx: str = "",
) -> str:
    """
    Fine-tunes a gpt-3.5 using provided data and conditions.

    Args:
    - input_file (str): Path to the input file containing experiment results.
    - condition (str): Condition to evaluate for extracting relevant results.
    - custom_function (str): Path or module containing the custom function used in the experiment.
    - system_prompt (str, optional): System message to prepend to each chat. Defaults to None.
    - model_suffix: (str, optional): Suffix to append to the model name. Defaults to None.

    Returns:
    - str: ID of the fine-tuned model.
    """

    code = read_code_from_path_or_module(custom_function)
    if not code:
        print("Failed to read code from path or module.")

        return ""

        return
    with open(input_file, 'rb') as f:
        result: Experiment = pickle.load(f)
    result_pairs = []
    for combo_result in result.combination_aggregated_metrics:
        results: List[ExperimentResult] = combo_result.experiment_results
        for rs in results:
            if rs.evaluator_outputs:
                for evaluator_output in rs.evaluator_outputs:
                    condition_met = evaluate_condition(
                        condition, evaluator_output
                    )
                    if condition_met:
                        result_pair = transform_experiment_result_generic(
                            code, rs
                        )
                        result_pairs.append(result_pair)

    formatted_data = _format_data_for_chatgpt_finetune(
        result_pairs, system_prompt
    )
    if validate_message(formatted_data):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        _print_stats(formatted_data)
        with open("tmp.jsonl", "w") as f:
            for entry in formatted_data:
                json_str = json.dumps(entry)
                f.write(json_str + "\n")

        with open("tmp.jsonl", "rb") as f:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            output = client.files.create(
                file=f,
                purpose="fine-tune",
            )
            print(output)
            while True:
                try:
                    model_details = client.fine_tuning.jobs.create(
                        training_file=output.id,
                        model="gpt-3.5-turbo",
                        suffix=model_suffx if model_suffx else ""
                    )
                    print("Fine-tuning job started: %s", model_details.id)
                    break
                except openai.BadRequestError as e:
                    print(e)
                    print("Waiting for file to be ready...")
                    time.sleep(60)

            ft_job = client.fine_tuning.jobs.retrieve(model_details.id)
            print(ft_job)
            while ft_job.status != "succeeded" and ft_job.status != "failed":
                ft_job = client.fine_tuning.jobs.retrieve(model_details.id)

                print(ft_job)
                time.sleep(60)

            print("Fine-tuning job finished: %s", model_details.id)
            return ft_job.fine_tuned_model  # type: ignore
        return ""
    else:
        print("Something is wrong, please check the data format.")
        return ""


def main():
    finetune(
        'test_demo_results.pkl',
        "name == openai_prompt_based_evaluator AND result >= 0 AND display_name == clarity",
    )


if __name__ == "__main__":
    main()
