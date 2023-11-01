"""Moudle for the gen subcommand.

This subcommand is used to generate the auto experiment configuration file with user input.
It will run the auto_prompt module to ask user for input and generate the configuration file.

Example:
    To run the auto prompt:
    $ yival gen

"""
import traceback
from argparse import ArgumentParser, Namespace
from ..auto_prompt.main import run_auto_gen

def add_arguments_to(subparser):
    """Add arguments to subcommand gen."""
    parser: ArgumentParser = subparser.add_parser(
        "gen", help=run_gen.__doc__
    )
    parser.description = run_gen.__doc__
    parser.set_defaults(func=run_gen)

    parser.add_argument(
        "--display",
        action="store_true",
        default=True,
        help="Display the results after the experiment."
    )


def run_gen(args: Namespace):
    """Run the auto generate task."""
    try:
        run_auto_gen()
        print("Auto prompt completed!")
    except Exception as excetion:
        print("Failed to run the auto generate.\nError:", str(excetion))
        traceback.print_exc()  # This will print the traceback
