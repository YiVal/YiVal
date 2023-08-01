# Contributing Guide

## Preparation

You need an Python 3.10+ environment with `poetry`.

For example, in Ubuntu 22.04, you can run:

```sh
sudo apt install python3-pip
sudo pip install poetry
```

## Setup

Initialize a Python virtual environment with `poetry`:

```sh
poetry install --sync
```

## Development

A vscode is recommended.
There are some configurations in `.vscode/` of this project.

## Test

```sh
pytest
```
