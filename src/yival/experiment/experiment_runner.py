from typing import List

from tqdm import tqdm

from ..configs.config_utils import load_and_validate_config
from ..logger.token_logger import TokenLogger
from ..schemas.experiment_config import ExperimentResult
from ..states.experiment_state import ExperimentState
from .data_processor import DataProcessor
from .display import display_results
from .evaluator import Evaluator
from .user_input import ExperimentInputApp
from .utils import (
    generate_experiment,
    register_custom_data_generator,
    register_custom_evaluators,
    register_custom_readers,
    register_custom_wrappers,
    run_single_input,
)


class ExperimentRunner:

    def __init__(self, config_path: str):
        self.config = load_and_validate_config(config_path)

    def run(self, display: bool = False, output_path: str = ""):
        results: List[ExperimentResult] = []
        register_custom_wrappers(
            self.config.get("custom_wrappers", {})  # type: ignore
        )
        register_custom_evaluators(
            self.config.get("custom_evaluators", {})  # type: ignore
        )
        register_custom_data_generator(
            self.config.get("custom_data_generators", {})  # type: ignore
        )
        evaluator = Evaluator(
            self.config.get("evaluators", [])  # type: ignore
        )

        logger = TokenLogger()
        # TODO support multi processing in the future
        state = ExperimentState.get_instance()
        state.set_experiment_config(self.config)
        state.active = True
        all_combinations = state.get_all_variation_combinations(
        )  # type: ignore
        if self.config["dataset"][  # type: ignore
            "source_type"
        ] == "dataset" or self.config[  # type: ignore
            "dataset"]["source_type"] == "machine_generated":  # type: ignore

            register_custom_readers(
                self.config.get("custom_readers", {})  # type: ignore
            )
            processor = DataProcessor(self.config["dataset"])  # type: ignore
            data_points = processor.process_data()
            for data in data_points:
                total_combinations = len(all_combinations) * len(data)
                with tqdm(
                    total=total_combinations, desc="Processing", unit="item"
                ) as pbar:
                    for d in data:
                        res = run_single_input(
                            d,
                            self.config,
                            all_combinations=all_combinations,
                            state=state,
                            logger=logger,
                            evaluator=evaluator
                        )
                        results.extend(res)
                        pbar.update(len(res))
            experiment = generate_experiment(results, evaluator)

            if display:
                display_results(experiment)

            if output_path:
                import json
                with open(output_path, "w") as file:
                    json.dump(experiment.asdict(), file)

        elif self.config["dataset"]["source_type"  # type: ignore
                                    ] == "user_input":
            app = ExperimentInputApp(
                self.config, all_combinations, state, logger, evaluator
            )
            app.run()


def main():
    runner = ExperimentRunner(config_path="demo/config.yml")
    runner.run()


if __name__ == "__main__":
    main()
