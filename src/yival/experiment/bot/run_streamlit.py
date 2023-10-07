# type: ignore
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
    for k, v in list(params.items()):
        if k == "yival_expected_result" and v is not None:
            expected_result = v
            params.pop(k)
        else:
            if v is not None:
                content[k] = v

    input_data = InputData(content=content, expected_result=expected_result)

    return input_data


def run_streamlit():
    with open("data.pkl", "rb") as f:
        data = pickle.load(f)
    experiment_data = data["experiment_data"]
    experiment_config = data["experiment_config"]
    function_args = data["function_args"]
    all_combinations = data["all_combinations"]
    logger = data["logger"]
    evaluator = data["evaluator"]
    # print(f"[DEBUG]all_combinations: {all_combinations}, type: {type(all_combinations)}")

    st.title("Chat With Yival!")
    combinations = [item['task'] for item in all_combinations]

    selected_combinations = st.multiselect(
        'Please select one or more combinations:', combinations
    )
    # print(f"[DEBUG]experiment_config: {experiment_config}")
    # experiment_config.all_combinations = selected_combinations

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
        print(f"[DEBUG]st.session_state.messages: {st.session_state.messages}")

        input_data = extract_params(prompt)
        print(f"[DEBUG]params: {input_data}")

        experiments: List[Experiment] = []
        results: List[ExperimentResult] = []

        lite_experiment_runner = LiteExperimentRunner(
            config=experiment_config,
            limiter=rate_limiter,
            data=[input_data],
            token_logger=logger,
            evaluator=evaluator
        )
        experiment = lite_experiment_runner.run_experiment(
            enable_selector=False
        )
        experiments.append(experiment)
        for exp in experiments:
            for res in exp.combination_aggregated_metrics:
                results.extend(res.experiment_results)

        st.session_state.messages.append({
            "role":
            "assistant",
            "content":
            f"Experiment result:{experiment}"
        })

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


if __name__ == "__main__":
    run_streamlit()
