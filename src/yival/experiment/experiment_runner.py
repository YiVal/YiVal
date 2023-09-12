import os
import pickle
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional

from tqdm import tqdm

from yival.experiment.app.app import display_results_dash  # type: ignore

from ..configs.config_utils import load_and_validate_config
from ..logger.token_logger import TokenLogger
from ..result_selectors.selection_context import SelectionContext
from ..schemas.experiment_config import Experiment, ExperimentResult
from ..states.experiment_state import ExperimentState
from .data_processor import DataProcessor
from .evaluator import Evaluator
from .rate_limiter import RateLimiter
from .utils import (
    generate_experiment,
    get_improver,
    get_selection_strategy,
    register_custom_data_generator,
    register_custom_evaluators,
    register_custom_improver,
    register_custom_readers,
    register_custom_selection_strategy,
    register_custom_variation_generators,
    register_custom_wrappers,
    run_single_input,
)

rate_limiter = RateLimiter(10 / 60)


class ExperimentRunner:

    def __init__(self, config_path: str):
        self.config = load_and_validate_config(config_path)

    def _register_custom_components(self):
        """Register custom components based on the configuration."""
        register_custom_wrappers(self.config.get("custom_wrappers", {}))
        register_custom_evaluators(self.config.get("custom_evaluators", {}))
        register_custom_data_generator(
            self.config.get("custom_data_generators", {})
        )
        register_custom_selection_strategy(
            self.config.get("custom_selection_strategy", {})
        )
        register_custom_improver(self.config.get("custom_improvers", {}))
        register_custom_variation_generators(
            self.config.get("custom_variation_generators", {})
        )

    def _process_dataset(self, all_combinations, state, logger,
                         evaluator) -> List[ExperimentResult]:
        """Process dataset source type and return the results."""
        results = []

        processor = DataProcessor(self.config["dataset"])  # type: ignore
        data_points = processor.process_data()

        for data in data_points:
            total_combinations = len(all_combinations) * len(data)
            with tqdm(
                total=total_combinations, desc="Processing", unit="item"
            ) as pbar:
                with ThreadPoolExecutor() as executor:
                    for res in executor.map(
                        self.parallel_task, data,
                        [all_combinations] * len(data), [ExperimentState.get_instance()] * len(data),
                        [logger] * len(data), [evaluator] * len(data)
                    ):
                        results.extend(res)
                        pbar.update(len(res))

        return results

    def parallel_task(
        self, data_point, all_combinations, state, logger, evaluator
    ):
        """Task to be run in parallel for processing data points."""
        RateLimiter(10 / 60)()  # Ensure rate limit
        return run_single_input(
            data_point,
            self.config,
            all_combinations=all_combinations,
            state=state,
            logger=logger,
            evaluator=evaluator
        )

    def run(
        self,
        display: bool = True,
        output_path: Optional[str] = "abc.pkl",
        experiment_input_path: Optional[str] = "abc.pkl"
    ):
        """Run the experiment based on the source type and provided configuration."""
        self._register_custom_components()

        evaluator = Evaluator(
            self.config.get("evaluators", [])  # type: ignore
        )  # type: ignore
        logger = TokenLogger()

        state = ExperimentState.get_default_state()
        state.set_experiment_config(self.config)
        state.active = True

        all_combinations = state.get_all_variation_combinations()

        source_type = self.config["dataset"]["source_type"]  # type: ignore
        if source_type in ["dataset", "machine_generated"]:  # type: ignore
            if experiment_input_path and os.path.exists(experiment_input_path):
                with open(experiment_input_path, 'rb') as file:
                    experiment: Experiment = pickle.load(file)
            else:
                register_custom_readers(
                    self.config.get("custom_reader", {})  # type: ignore
                )  # type: ignore
                results = self._process_dataset(
                    all_combinations, state, logger, evaluator
                )
                experiment = generate_experiment(
                    results, evaluator
                )  # type: ignore

                strategy = get_selection_strategy(self.config)
                if strategy:
                    context_trade_off = SelectionContext(strategy=strategy)
                    experiment.selection_output = context_trade_off.execute_selection( # type: ignore
                        experiment=experiment
                    )

                improver = get_improver(self.config)
                print(f"[INFO] improver: {improver}")
                if improver:
                    print("[INFO] improve")
                    experiment.improver_output = improver.improve(
                        experiment, self.config, evaluator, logger
                    )

            if output_path:
                with open(output_path, 'wb') as file:
                    pickle.dump(experiment, file)

            if display:
                display_results_dash(
                    experiment, self.config, all_combinations, ExperimentState.get_instance(), logger,
                    evaluator
                )

        elif source_type == "user_input":
            display_results_dash(
                Experiment([], []), self.config, all_combinations, ExperimentState.get_instance(),
                logger, evaluator, True
            )


# def main():
#     runner = ExperimentRunner(config_path="demo/config.yml")
#     runner.run()

# if __name__ == "__main__":
#     main()
