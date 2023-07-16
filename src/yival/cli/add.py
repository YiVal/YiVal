"""An example CLI subcommand."""

from argparse import ArgumentParser, Namespace

from .. import api


def add_arguments_to(subparser):
    """Add arguments to subcommand add."""
    parser: ArgumentParser = subparser.add_parser("add", help=add.__doc__)
    parser.description = add.__doc__
    parser.set_defaults(func=add)

    parser.add_argument("one", type=int, help="The 1st number.")
    parser.add_argument("another", type=int, help="The 2nd number.")


def add(args: Namespace):
    """Add 2 numbers."""
    value = api.add(args.one, args.another)
    print(value)
