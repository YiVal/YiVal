# type: ignore
import io
import json
import os
import pickle
import re

import streamlit as st

from yival.combination_improvers.lite_experiment import LiteExperimentRunner
from yival.experiment.rate_limiter import RateLimiter
from yival.schemas.common_structures import InputData

rate_limiter = RateLimiter(60 / 60)


def extract_params(input_str):
    pattern = r"([\w\s]+)( \(Optional\))?:\s*\{(.*?)\}"
    matches = re.findall(pattern, input_str)
    params = {match[0].strip(): match[2] for match in matches}

    expected_result = None
    content = {}
    example_id = 0
    for k, v in list(params.items()):
        if k == "yival_expected_result" and v is not None:
            expected_result = v
            params.pop(k)
        else:
            if v is not None:
                content[k] = v

    input_data = InputData(content=content, expected_result=expected_result)

    return input_data


def display_image(image_list):
    images = image_list
    image_data = []
    for image in images:
        byte_stream = io.BytesIO()
        image.save(byte_stream, format='PNG')
        byte_data = byte_stream.getvalue()
        image_data.append(byte_data)

    st.image(
        image_data,
        caption=["Image 1", "Image 2", "Image 3", "Image 4"],
        use_column_width=False
    )


def extract_params(input_str):
    pattern = r"([\w\s]+)( \(Optional\))?:\s*\{(.*?)\}"
    matches = re.findall(pattern, input_str)
    params = {match[0].strip(): match[2] for match in matches}

    expected_result = None
    content = {}
    example_id = 0
    for k, v in list(params.items()):
        if k == "yival_expected_result" and v is not None:
            expected_result = v
            example_id += 1
            params.pop(k)
        else:
            if v is not None:
                content[k] = v

    input_data = InputData(content=content, expected_result=expected_result)

    return input_data


def run_experiments(
    selected_combinations, input_data, experiment_config, logger, evaluator
):
    """
    Run the experiment with lite_experiment
    """
    experiments: List[Experiment] = []
    results: List[ExperimentResult] = []

    lite_experiment_runner = LiteExperimentRunner(
        config=experiment_config,
        limiter=rate_limiter,
        data=[input_data],
        token_logger=logger,
        evaluator=evaluator
    )
    lite_experiment_runner.set_variations(selected_combinations)
    experiment = lite_experiment_runner.run_experiment(enable_selector=False)
    experiments.append(experiment)
    for exp in experiments:
        for res in exp.combination_aggregated_metrics:
            results.extend(res.experiment_results)

    return results


def display_results(results):
    """
    Display the results with bot messages after the experiment.
    """
    for result in results:
        bot_reply = f"Result to your task: \"{list(result.combination.values())[0]}\" is as follows:\n \n"

        if result.raw_output.text_output:
            bot_reply += f"- Text Result: {result.raw_output.text_output}\n \n"

        if result.latency:
            bot_reply += f"- Latency: {result.latency}\n \n"

        if result.token_usage:
            bot_reply += f"- Token Usage: {result.token_usage}\n \n"

        if result.evaluator_outputs:
            bot_reply += "- Evaluator:\n \n"
            for output in result.evaluator_outputs:
                bot_reply += f"\t- {output.name}: {output.result}\n \n"

        st.session_state.messages.append({
            "role": "assistant",
            "content": bot_reply
        })

        if result.raw_output.image_output:
            display_image(result.raw_output.image_output)


def run_streamlit():
    """
    Run the experiment using the user input and pkl file.
    """

    with open("data.pkl", "rb") as f:
        data = pickle.load(f)
    experiment_data = data["experiment_data"]
    experiment_config = data["experiment_config"]
    function_args = data["function_args"]
    all_combinations = data["all_combinations"]
    logger = data["logger"]
    evaluator = data["evaluator"]
    for combination in all_combinations:
        for key in combination:
            combination[key] = [combination[key]]

    st.title("Chat With Yival!")

    selected_combinations = st.multiselect(
        'Please select one or more combinations:', all_combinations
    )

    args = [arg for arg in function_args.keys()]
    args_message = ', '.join([f'{arg}: {{content}}' for arg in args])
    hint_message = f'Please input parameters as this format:\n {args_message}.'

    if 'messages' not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant",
            "content": hint_message
        })

    if prompt := st.chat_input(f"{args_message}"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        input_data = extract_params(prompt)
        results = run_experiments(
            selected_combinations, input_data, experiment_config, logger,
            evaluator
        )
        display_results(results)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


if __name__ == "__main__":
    run_streamlit()
