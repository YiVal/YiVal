"""Moudle for the gen subcommand.

This subcommand is used to generate the auto experiment configuration file with user input.
It will run the auto_prompt module to ask user for input and generate the configuration file.

Example:
    To run the auto prompt:
    $ yival task

"""
import traceback
from argparse import ArgumentParser, Namespace

from ..auto_prompt.main import run_auto_gen, run_demo


def add_arguments_to(subparser):
    """Add arguments to subcommand task."""
    parser: ArgumentParser = subparser.add_parser(
        "task", help=run_task.__doc__
    )
    parser.description = run_task.__doc__
    parser.set_defaults(func=run_task)

    parser.add_argument(
        "--display",
        action="store_true",
        default=True,
        help="Display the results after the experiment."
    )


def run_task(args: Namespace):
    """Run the auto generate task."""
    try:
        run_demo()
        print("Auto prompt completed!")
    except Exception as excetion:
        print("Failed to run the auto generate.\nError:", str(excetion))
        traceback.print_exc()  # This will print the traceback
