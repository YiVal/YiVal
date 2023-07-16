"""Evaluate and refine AI models."""

import sys
from argparse import ArgumentParser, Namespace

from yival.cli import add_subcommands_to


def _default(_: Namespace) -> int:
    return 1


def main():
    """The entry of CLI yival."""
    parser = ArgumentParser()
    parser.set_defaults(func=_default)
    add_subcommands_to(parser)

    args = parser.parse_args()

    status = args.func(args)
    sys.exit(status)


if __name__ == "__main__":
    main()
