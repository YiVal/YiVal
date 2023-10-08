import traceback
from argparse import ArgumentParser, Namespace

from ..experiment.experiment_runner import ExperimentRunner


def add_arguments_to(subparser):
    """Add arguments to subcommand run."""
    parser: ArgumentParser = subparser.add_parser(
        "bot", help=run_experiment.__doc__
    )
    parser.description = run_experiment.__doc__
    parser.set_defaults(func=run_experiment)

    parser.add_argument(
        "config_path", type=str, help="Path to the YAML configuration file."
    )

    parser.add_argument(
        "--display",
        action="store_true",
        default=False,
        help="Display the results after the experiment."
    )

    parser.add_argument(
        "--interactive",
        action="store_true",
        default=True,
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
    except Exception as e:
        print("Failed to run the experiment.\nError:", str(e))
        traceback.print_exc()  # This will print the traceback
