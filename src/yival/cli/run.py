"""Run."""

from argparse import ArgumentParser, Namespace


def add_arguments_to(subparser):
    """Add arguments to subcommand run."""
    parser: ArgumentParser = subparser.add_parser("run", help=run.__doc__)
    parser.description = run.__doc__
    parser.set_defaults(func=run)

    # Add arguments here.


def run(args: Namespace):
    """Run."""
    print(f"TODO: {args}")
