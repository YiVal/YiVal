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
    runner = ExperimentRunner(config_path="path/to/config")
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

from ..configs.config_utils import load_and_validate_config
from .data_processor import DataProcessor
from .utils import register_custom_readers


class ExperimentRunner:
    """
    A class to execute experiments based on user-defined functions and configurations.

    This runner orchestrates the end-to-end flow of experiments, from processing
    input data to evaluating and saving the results.

    Attributes:
    ----------
    config : Dict
        The loaded and validated configuration for the experiment.

    Methods:
    -------
    run():
        Executes the experiment based on the provided user function and configuration.
    """

    def __init__(self, config_path: str):
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
        if self.config["dataset"]["source_type"] == "dataset":
            register_custom_readers(self.config.get("custom_readers", {}))
            processor = DataProcessor(self.config["dataset"])
            for data in processor.process_data():
                print(data)

        # Parallel processing of user function
        # ...

        # Run outputs through evaluators
        # ...

        # Save results based on OutputConfig
        # ...

        # Return merged results
        # ...
        pass


def main():
    runner = ExperimentRunner(config_path="/Users/taofeng/YiVal/config.yml")
    runner.run()


if __name__ == "__main__":
    main()
