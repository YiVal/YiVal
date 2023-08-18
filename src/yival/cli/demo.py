import os
import shutil
from argparse import ArgumentParser, Namespace

from .run import run_experiment


def add_arguments_to(subparser):
    """Add arguments to subcommand validate."""
    parser: ArgumentParser = subparser.add_parser("demo", help=demo.__doc__)
    parser.description = demo.__doc__
    parser.set_defaults(func=demo)

    parser.add_argument(
        "--basic_interactive",
        action="store_true",
        default=True,
        help="Use the translation example to demo the interactive mode"
    )


def demo(args: Namespace):
    """Demo usage of YiVal"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if args.basic_interactive:
        src_path = os.path.join(
            base_dir, '../demo/configs/basic_interactive_config.yml'
        )
        dest_path = './basic_interactive_config.yml'
        shutil.copy(src_path, dest_path)
        print(f"Copied {src_path} to {dest_path}")
        run_args = Namespace(
            config_path=dest_path,
            display=True,
            output_path="",
            experiment_input_path=""
        )
        run_experiment(run_args)
