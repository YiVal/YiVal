"""The CLI subcommands."""

from argparse import ArgumentParser

from .init import add_arguments_to as INIT
from .validate import add_arguments_to as RUN


def add_subcommands_to(parser: ArgumentParser):
    """Add subcommands to the main parser."""
    subparser = parser.add_subparsers(title="actions")

    for func in (
        INIT,
        RUN,
    ):
        func(subparser)
