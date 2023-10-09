# Contributing Guide

## Preparation

You need an Python 3.10+ environment with [poetry].

!!! Example
    === "Linux"
        For example, in Ubuntu 22.04, you can run:

        ```sh
        sudo apt install python3-pip
        sudo pip install poetry
        ```
    === "Mac OS"
        ```sh
        brew install python@3.10

        brew install poetry
        # Or
        python3 -m pip install --user poetry
        ```
    === "Windows"
        Download exe installer from python.org, or use [Chocolatey] :

        ```sh
        choco install python
        python3 -m pip install poetry
        ```

        There should be a reboot.
    === "Other"
        See [poetry] document for installation guide.

## Setup

Initialize a Python virtual environment with `poetry`:

<!-- markdownlint-disable MD046 -->
```sh
poetry install --sync
```

## Development

A vscode is recommended.
There are some configurations in `.vscode/` of this project.

The commands below should be executed inside `poetry shell`,
or with prefix `poetry run`.

## Test

```sh
pytest
```

## Mkdocs

Preview the docs locally:

```sh
mkdocs serve
```

--8<-- "docs/_include/links.md"
