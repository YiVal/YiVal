from argparse import ArgumentParser, Namespace

import yaml

from ..configs.config_utils import ExperimentConfig


def add_arguments_to(subparser):
    """Add arguments to subcommand validate."""
    parser: ArgumentParser = subparser.add_parser(
        "validate", help=validate.__doc__
    )
    parser.description = validate.__doc__
    parser.set_defaults(func=validate)

    parser.add_argument(
        "config_file",
        type=str,
        help="Path to the YAML configuration file to validate."
    )


def validate(args: Namespace):
    """Validate the provided YAML configuration file."""
    with open(args.config_file, 'r') as f:
        config_data = yaml.safe_load(f)

    try:
        # Convert the dictionary into the ExperimentConfig dataclass
        ExperimentConfig(**config_data)
        print(f"Configuration file {args.config_file} is valid!")
    except Exception as e:
        print(f"Validation failed for {args.config_file}.\nError: {e}")
