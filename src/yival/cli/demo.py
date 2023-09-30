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
        default=False,
        help="Use the translation example to demo the interactive mode"
    )

    parser.add_argument(
        "--qa_expected_results",
        action="store_true",
        default=False,
        help=
        "Use the question asnwering to demo the input from data set and use expected_results_evaluators."
    )

    parser.add_argument(
        "--auto_prompts",
        action="store_true",
        default=False,
        help=
        "Automatically generate prompts and test data for tech startup landing page headline."
    )

    parser.add_argument(
        "--async_eval",
        type=bool,
        default=False,
        help="Whether the custom function is async"
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
            experiment_input_path="",
            async_eval=args.async_eval
        )
    elif args.qa_expected_results:
        src_path = os.path.join(
            base_dir, '../demo/configs/qa_expected_results_config.yml'
        )
        dest_path = './qa_expected_results_config.yml'
        shutil.copy(src_path, dest_path)
        print(f"Copied {src_path} to {dest_path}")
        run_args = Namespace(
            config_path=dest_path,
            display=True,
            output_path="",
            experiment_input_path="",
            async_eval=args.async_eval
        )
    elif args.auto_prompts:
        src_path = os.path.join(
            base_dir, '../demo/configs/auto_prompts_config.yml'
        )
        dest_path = './auto_prompts_config.yml'
        shutil.copy(src_path, dest_path)
        print(f"Copied {src_path} to {dest_path}")
        run_args = Namespace(
            config_path=dest_path,
            display=True,
            output_path="demo_results.pkl",
            experiment_input_path="",
            async_eval=args.async_eval
        )
    run_experiment(run_args)
