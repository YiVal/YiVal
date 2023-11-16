import argparse
import asyncio
import re
import subprocess

from termcolor import colored

from yival import logger
from yival.common.auto_cofig_utils import auto_generate_config
from yival.experiment import evaluator
from yival.experiment.app.app import display_results_dash  # type: ignore
from yival.schemas.experiment_config import Experiment
from yival.states.experiment_state import ExperimentState

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
    # Identify variables annotated with {} and replace spaces with underscores
    formatted = re.sub(
        r'\{([^}]*)\}', lambda m: m.group(1).replace(" ", "_"), input_str
    )
    return formatted


def run_auto_gen():
    display_results_dash(
        Experiment([], []),
        None, [],
        ExperimentState.get_instance(),
        logger,
        evaluator,
        True,
        True,
        False,
        port=8050
    )
    print(colored("\nProcess completed!", "green"))


def run_demo():
    display_results_dash(
        Experiment([], []),
        None, [],
        ExperimentState.get_instance(),
        logger,
        evaluator,
        True,
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

    name = input("Please enter the name of the experiment: ")
    # Directly read the prompt and evaluation aspects using input()
    prompt_input = input(
        "Please enter the prompt (use {{}} to wrap around input variables): "
    )
    evaluation_aspects_input = input(
        "Please provide evaluation aspects (optional): "
    )

    aspects = evaluation_aspects_input.split(
        ","
    ) if evaluation_aspects_input else []

    asyncio.run(auto_generate_config(prompt_input, aspects))

    print(colored("\nGenerating configuration...", "yellow"))

    subprocess.run([
        "yival", "run", "auto_generated_config.yaml",
        f"--output_path={name}.pkl"
    ])

    print(colored("\nProcess completed!", "green"))


if __name__ == "__main__":
    main()
