import argparse
import subprocess

from termcolor import colored

from yival import logger
from yival.common.auto_cofig_utils import auto_generate_config
from yival.experiment import evaluator
from yival.experiment.app.app import display_results_dash  # type: ignore

from ..schemas.experiment_config import Experiment
from ..states.experiment_state import ExperimentState

try:
    import inquirer
except ImportError:
    print(
        colored(
            "Please install the 'inquirer' module for interactive prompts.",
            "red"
        )
    )
    exit(1)


def format_input(input_str):
    return input_str.replace(" ", "_")


def run_auto_gen():
    display_results_dash(
        Experiment([], []),
        None, [],
        ExperimentState.get_instance(),
        logger,
        evaluator,
        True,
        True,
        port=8050
    )
    print(colored("\nProcess completed!", "green"))


def main():
    parser = argparse.ArgumentParser(
        description="Auto Generate Configuration for Yival."
    )
    parser.parse_args()

    questions = [
        inquirer.Text('task', message="What task would you like to set up?"),
        inquirer.Text(
            'context_info',
            message=
            "Provide input for the task, separated by comma. For example: 'team' or 'project'."
        ),
        inquirer.Text(
            'evaluation_aspects',
            message="Please provide evaluation aspects (optional)"
        ),
    ]

    answers = inquirer.prompt(questions)

    parameters = answers['context_info'].split(",")
    aspect = []
    if answers['evaluation_aspects']:
        aspect = answers['evaluation_aspects'].split(",")

    auto_generate_config(answers['task'], parameters, aspect)

    print(colored("\nGenerating configuration...", "yellow"))

    subprocess.run([
        "yival", "run", "auto_generated_config.yaml",
        "--output_path=auto_generated.pkl"
    ])

    print(colored("\nProcess completed!", "green"))


if __name__ == "__main__":
    main()
