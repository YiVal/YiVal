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
        help="Display the results after the experiment."
    )

    parser.add_argument(
        "--output_path",
        type=str,
        default=None,
        help="Path to store the experiment results."
    )


def run_experiment(args: Namespace):
    """Run the experiment using the provided YAML configuration file."""
    try:
        runner = ExperimentRunner(args.config_path)
        runner.run(display=args.display, output_path=args.output_path)
        print("Experiment completed!")
    except Exception as e:
        print(f"Failed to run the experiment.\nError: {e}")
