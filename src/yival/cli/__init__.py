"""The CLI subcommands."""

from argparse import ArgumentParser

from .bot import add_arguments_to as BOT
from .demo import add_arguments_to as DEMO
from .init import add_arguments_to as INIT
from .run import add_arguments_to as RUN
from .validate import add_arguments_to as VALIDATE
from .gen import add_arguments_to as GEN


def add_subcommands_to(parser: ArgumentParser):
    """Add subcommands to the main parser."""
    subparser = parser.add_subparsers(title="actions")

    for func in (
        INIT,
        VALIDATE,
        RUN,
        DEMO,
        BOT,
        GEN,
    ):
        func(subparser)
