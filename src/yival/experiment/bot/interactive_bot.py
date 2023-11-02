# type: ignore

import os
import pickle

from yival.experiment.utils import get_function_args
from yival.schemas.experiment_config import Experiment


def interactive_bot(
    experiment_data: Experiment,
    experiment_config,
    all_combinations,
    state,
    logger,
    evaluator,
    interactive=True,
):
    print("Running interactive bot mode...")
    if experiment_data.enhancer_output:
        for group_result in experiment_data.enhancer_output.group_experiment_results:
            experiment_results = []
            seen = set()
            for r in group_result.experiment_results:
                if str(r.combination) in seen:
                    continue
                else:
                    seen.add(str(r.combination))
                    experiment_results.append(r)
            group_result.experiment_results = experiment_results
    function_args = get_function_args(
        experiment_config["custom_function"], experiment_config["dataset"]
    )
    function_args["yival_expected_result (Optional)"] = 'str'

    data = {
        "experiment_data": experiment_data,
        "experiment_config": experiment_config,
        "function_args": function_args,
        "all_combinations": all_combinations,
        "state": state,
        "logger": logger,
        "evaluator": evaluator,
        "interactive": interactive,
    }
    with open("data.pkl", "wb") as f:
        pickle.dump(data, f)

    os.system("streamlit run src/yival/experiment/bot/run_streamlit.py")


if __name__ == "__main__":
    pass
