"""
Experiment Runner Module
========================

This module provides the `ExperimentRunner` class to orchestrate end-to-end experiments.
It allows users to define a function and a configuration, and then handles the
execution, evaluation, and storage of results.

Key Features:
-------------
- Load and validate experiment configurations.
- Process input data based on user-provided DatasetConfig.
- Parallel execution of user-defined functions.
- Evaluate results using various evaluators.
- Store results as specified in the OutputConfig.

Usage:
------
    user_function = ...
    runner = ExperimentRunner(user_func=user_function, config_path="path/to/config")
    results = runner.run()

Classes:
--------
- `ExperimentRunner`: Class to manage and execute experiments.

Dependencies:
-------------
- `load_and_validate_config`: Function from the `config_utils` module to load and
   validate experiment configurations.

Note:
-----
This module is a part of the YiVal project, an innovative open-source framework for AI
model evaluations.

"""

from typing import Callable

from ..configs.config_utils import load_and_validate_config


class ExperimentRunner:
    """
    A class to execute experiments based on user-defined functions and configurations.

    This runner orchestrates the end-to-end flow of experiments, from processing
    input data to evaluating and saving the results.

    Attributes:
    ----------
    user_func : Callable
        The user-defined function to be executed as part of the experiment.
    config : Dict
        The loaded and validated configuration for the experiment.

    Methods:
    -------
    run():
        Executes the experiment based on the provided user function and configuration.
    """

    def __init__(self, user_func: Callable, config_path: str):
        self.user_func = user_func
        self.config = load_and_validate_config(config_path)

    def run(self):
        """
        Executes the experiment.

        This method carries out the following steps:
        1. Processes data based on the provided DatasetConfig.
        2. Executes the user function in parallel (if applicable).
        3. Evaluates the results using the configured evaluators.
        4. Saves the results as per the OutputConfig.
        5. Returns the merged results from all evaluators.

        Returns:
        --------
        Any
            The merged results from all evaluators.
        """
        # Process data based on DatasetConfig
        # ...

        # Parallel processing of user function
        # ...

        # Run outputs through evaluators
        # ...

        # Save results based on OutputConfig
        # ...

        # Return merged results
        # ...
        pass
