"""The CLI subcommands."""

from argparse import ArgumentParser

from .add import add_arguments_to as ADD
from .run import add_arguments_to as RUN


def add_subcommands_to(parser: ArgumentParser):
    """Add subcommands to the main parser."""
    subparser = parser.add_subparsers(title="actions")

    for func in (
        ADD,
        RUN,
    ):
        func(subparser)
