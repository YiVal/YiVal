"""Module for running experiments.

This module provides functionality for setting up and running experiments
based on a YAML configuration file. It defines command-line arguments for
specifying various settings such as display options and output paths.

Example:
    To run an experiment using a configuration file 'config.yml':
    $ yival run config.yml
"""
import traceback
from argparse import ArgumentParser, Namespace

from ..experiment.experiment_runner import ExperimentRunner


def add_arguments_to(subparser):
    """Add arguments to subcommand run."""
    parser: ArgumentParser = subparser.add_parser(
        "run", help=run_experiment.__doc__
    )
    parser.description = run_experiment.__doc__
    parser.set_defaults(func=run_experiment)

    parser.add_argument(
        "config_path", type=str, help="Path to the YAML configuration file."
    )

    parser.add_argument(
        "--display",
        action="store_true",
        default=True,
        help="Display the results after the experiment."
    )

    parser.add_argument(
        "--interactive",
        action="store_true",
        default=False,
        help="Open interactive mode to use a chatbot."
    )

    parser.add_argument(
        "--output_path",
        type=str,
        default="",
        help="Path to store the experiment results."
    )

    parser.add_argument(
        "--experiment_input_path",
        type=str,
        default="",
        help="Path to existing experiment results."
    )

    parser.add_argument(
        "--async_eval",
        type=bool,
        default=False,
        help="Whether the custom function is async"
    )


def run_experiment(args: Namespace):
    """Run the experiment using the provided YAML configuration file."""
    try:
        runner = ExperimentRunner(args.config_path)
        runner.run(
            display=args.display,
            interactive=args.interactive,
            output_path=args.output_path,
            experiment_input_path=args.experiment_input_path,
            async_eval=args.async_eval
        )
        print("Experiment completed!")
    except Exception as excetion:
        print("Failed to run the experiment.\nError:", str(excetion))
        traceback.print_exc()  # This will print the traceback
