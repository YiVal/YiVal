import json
import os
import pickle
import time
from typing import Dict, List

import replicate
import requests

from yival.dataset.data_utils import (
    evaluate_condition,
    read_code_from_path_or_module,
    transform_experiment_result_generic,
)
from yival.schemas.experiment_config import Experiment, ExperimentResult


def _format_data_for_replicate_finetune(data: list[dict[str, str]]):
    formatted_data = []

    for entry in data:
        chat_entry: dict[str, str] = {}
        prompt = ""
        if "Instruction" in entry:
            prompt += entry["Instruction"] + "\n"

        prompt += entry["Input"]
        chat_entry.update({"prompt": prompt, "completion": entry["Output"]})

        formatted_data.append(chat_entry)

    return formatted_data


def _extract_from_input_data(result: Experiment) -> List[Dict[str, str]]:
    result_pairs = []
    for rs in result.group_experiment_results:
        input_data = json.loads(rs.group_key)
        finetune_data = {
            "prompt":
            "Translate the following english to chinese" + "\n" +
            input_data['content']['teacher_quiz'],
            "completion":
            input_data['expected_result']
        }
        result_pairs.append(finetune_data)

    return result_pairs


def finetune(
    input_file: str,
    condition: str,
    custom_function: str,
    destination: str,
    model_name: str,
    num_train_epochs: int = 3,
    support_expected_value: bool = False,
    system_prompt: str = "",
) -> str:
    """
    Fine-tunes a replicate model using provided data and conditions.

    Args:
    - input_file (str): Path to the input file containing experiment results.
    - condition (str): Condition to evaluate for extracting relevant results.
    - custom_function (str): Path or module containing the custom function used in the experiment.
    - destination: (str): The model to push the trained version to .
    - model_name: (str): Model name that will be used for finetune.
    - num_train_epochs: (int, optional): Number of epochs to train the model.
    - system_prompt (str, optional): System message to prepend to each chat. Defaults to None.

    Returns:
    - str: ID of the fine-tuned model.
    """

    code = read_code_from_path_or_module(custom_function)
    if not code:
        print("Failed to read code from path or module.")
        return ""

    with open(input_file, 'rb') as f:
        result: Experiment = pickle.load(f)

    if support_expected_value:
        formatted_data = _extract_from_input_data(result)
    else:
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

        formatted_data = _format_data_for_replicate_finetune(result_pairs)

    headers = {"Authorization": f"Token {os.environ['REPLICATE_API_TOKEN']}"}

    with open("data.jsonl", "w", encoding='utf-8') as f:
        for entry in formatted_data:
            json_str = json.dumps(entry, separators=(',', ':'))
            f.write(json_str + "\n")

    response = requests.post(
        "https://dreambooth-api-experimental.replicate.com/v1/upload/data.jsonl",
        headers=headers
    )
    response_data = response.json()

    # Extract upload_url from the response and make PUT request
    upload_url = response_data["upload_url"]
    with open("data.jsonl", "rb") as file:
        headers = {"Content-Type": "application/jsonl"}
        requests.put(upload_url, headers=headers, data=file)

    # Extract serving_url from the response
    serving_url = response_data["serving_url"]
    print(serving_url)

    training = replicate.trainings.create(
        version=model_name,
        input={
            "train_data": serving_url,
            "num_train_epochs": num_train_epochs,
        },
        destination=destination,
    )
    print(training)
    while True:
        training = replicate.trainings.get(training.id)
        print(training.status)
        if training.status == "succeeded":
            print(training.output)
            return training.output
        elif training.status == "failed":
            print("Training failed.")
            return ""
        else:
            print("Waiting for training to complete...")
            time.sleep(60)


def headline_generation():
    finetune(
        'headline.pkl',
        "name == openai_prompt_based_evaluator AND result >= 0 AND display_name == clear",
        "yival.demo.headline_generation",
        "yival/llama2",
        "meta/llama-2-7b-chat:8e6975e5ed6174911a6ff3d60540dfd4844201974602551e10e9e87ab143d81e",
    )


def teacher_quiz():
    finetune(
        "quiz", "", "yival.demo.headline_generation", "yival/llama2",
        "meta/llama-2-7b-chat:8e6975e5ed6174911a6ff3d60540dfd4844201974602551e10e9e87ab143d81e",
        3, True
    )


if __name__ == "__main__":
    teacher_quiz()
