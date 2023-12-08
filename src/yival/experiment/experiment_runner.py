import asyncio
import os
import pickle
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from typing import List, Optional

from tqdm import tqdm

import yival.common.utils as common
from yival.configs.config_utils import load_and_validate_configs
from yival.experiment.app.app import display_results_dash  # type: ignore
from yival.experiment.bot.interactive_bot import interactive_bot  # type: ignore

from ..logger.token_logger import TokenLogger
from ..result_selectors.selection_context import SelectionContext
from ..schemas.experiment_config import Experiment, ExperimentResult
from ..states.experiment_state import ExperimentState
from .data_processor import DataProcessor
from .evaluator import Evaluator
from .rate_limiter import RateLimiter
from .utils import (
    arun_single_input,
    generate_experiment,
    get_enhancer,
    get_selection_strategy,
    get_trainer,
    register_custom_data_generator,
    register_custom_enhancer,
    register_custom_evaluators,
    register_custom_readers,
    register_custom_selection_strategy,
    register_custom_variation_generators,
    register_custom_wrappers,
    run_single_input,
)

rate_limiter = RateLimiter(10 / 60)


class ExperimentRunner:

    def __init__(self, config_path: str):
        self.configs = load_and_validate_configs(config_path)

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
        register_custom_enhancer(self.config.get("custom_enhancers", {}))
        register_custom_variation_generators(
            self.config.get("custom_variation_generators", {})
        )

    async def _aprocess_dataset(self, all_combinations, logger,
                                evaluator) -> List[ExperimentResult]:
        processor = DataProcessor(self.config["dataset"])  # type: ignore
        data_batches = list(processor.process_data())
        sum([len(batch) for batch in data_batches]) * len(all_combinations)
        semaphore = asyncio.Semaphore(20)
        total_tasks = sum([len(batch)
                           for batch in data_batches]) * len(all_combinations)
        if "custom_function" not in self.config or not self.config[  # type: ignore
            "custom_function"]:
            return []
        rate_limiter = common.RateLimiter(100 / 60, 10000)

        async def eval_fn_with_semaphore(data_point):
            async with semaphore:
                while True:
                    await rate_limiter.wait()
                    try:
                        results = await self.aparallel_task(
                            data_point, all_combinations, logger, evaluator
                        )
                        if results:
                            for result in results:
                                rate_limiter.add_tokens(result.token_usage)
                        return results
                    except:
                        print("Rate limit exceeded, sleeping...")
                        await asyncio.sleep(100)

        futures = []
        results = []
        for data_batch in data_batches:
            for data in data_batch:
                futures.append(
                    asyncio.ensure_future(eval_fn_with_semaphore(data))
                )

        for future in tqdm(
            asyncio.as_completed(futures), total=total_tasks, disable=False
        ):
            results.extend(await future)

        return results

    def _process_dataset(self, all_combinations, logger,
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
                with ThreadPoolExecutor(max_workers=10) as executor:
                    for res in executor.map(
                        self.parallel_task, data,
                        [all_combinations] * len(data), [logger] * len(data),
                        [evaluator] * len(data)
                    ):
                        results.extend(res)
                        pbar.update(len(res))

        return results

    async def aparallel_task(
        self, data_point, all_combinations, logger, evaluator
    ):
        for _ in all_combinations:
            return await arun_single_input(
                data_point,
                self.config,
                all_combinations=all_combinations,
                logger=logger,
                evaluator=evaluator
            )

    def parallel_task(self, data_point, all_combinations, logger, evaluator):
        """Task to be run in parallel for processing data points."""
        RateLimiter(1000 / 60)()  # Ensure rate limit
        return run_single_input(
            data_point,
            self.config,
            all_combinations=all_combinations,
            logger=logger,
            evaluator=evaluator
        )

    def run(
        self,
        display: bool = True,
        interactive: bool = False,
        output_path: Optional[str] = "abc.pkl",
        experiment_input_path: Optional[str] = "abc.pkl",
        async_eval: bool = False,
        enhance_page: bool = False
    ):
        """Run the experiment based on the source type and provided configuration."""
        base_port = 8074
        display_threads = []
        for idx, config in enumerate(self.configs):
            self.config = config

            enable_custom_func = "custom_function" in self.config  #type: ignore
            config_experiment_input_path = ""
            if output_path:
                config_output_path = f"{os.path.splitext(output_path)[0]}_{idx}.pkl"
            if experiment_input_path:
                config_experiment_input_path = f"{os.path.splitext(experiment_input_path)[0]}_{idx}.pkl"
            self._register_custom_components()

            evaluator = Evaluator(
                self.config.get("evaluators", [])  # type: ignore
            )  # type: ignore
            logger = TokenLogger()

            state = ExperimentState()
            state.set_experiment_config(self.config)
            state.active = True

            all_combinations = state.get_all_variation_combinations()

            source_type = self.config["dataset"]["source_type"]  # type: ignore
            if source_type in ["dataset", "machine_generated"]:  # type: ignore
                if config_experiment_input_path and os.path.exists(
                    config_experiment_input_path
                ):
                    with open(config_experiment_input_path, 'rb') as file:
                        experiment: Experiment = pickle.load(file)
                else:
                    register_custom_readers(
                        self.config.get("custom_reader", {})  # type: ignore
                    )  # type: ignore
                    if async_eval:
                        results = asyncio.run(
                            self._aprocess_dataset(
                                all_combinations, logger, evaluator
                            )
                        )
                    else:
                        results = self._process_dataset(
                            all_combinations, logger, evaluator
                        )

                    #results res is None if custom_func not provided
                    experiment = generate_experiment(
                        results, evaluator
                    )  # type: ignore
                    strategy = get_selection_strategy(self.config)
                    if strategy and enable_custom_func:
                        context_trade_off = SelectionContext(strategy=strategy)
                        experiment.selection_output = context_trade_off.execute_selection( # type: ignore
                            experiment=experiment
                        )

                    enhancer = get_enhancer(self.config)
                    if enhancer and enable_custom_func:
                        experiment.enhancer_output = enhancer.enhance(
                            experiment, self.config, evaluator, logger
                        )

                    trainer = get_trainer(self.config)
                    if trainer:
                        trainer.train(experiment, self.config)

                if output_path:
                    with open(config_output_path, 'wb') as file:
                        pickle.dump(experiment, file)
                if display and enable_custom_func:
                    t = Thread(
                        target=display_results_dash,
                        args=(
                            experiment, self.config, all_combinations,
                            ExperimentState.get_instance(), logger, evaluator,
                            enhance_page
                        ),
                        kwargs={"port": base_port + idx}
                    )
                    display_threads.append(t)
                    t.start()
                if interactive:
                    interactive_bot(
                        experiment, self.config, all_combinations,
                        ExperimentState.get_instance(), logger, evaluator
                    )
            elif source_type == "user_input":
                display_results_dash(
                    Experiment([], []), self.config, all_combinations,
                    ExperimentState.get_instance(), logger, evaluator, False,
                    True, False, False, False
                )
        for t in display_threads:
            t.join()


# def main():
#     runner = ExperimentRunner(config_path="demo/config.yml")
#     runner.run()

# if __name__ == "__main__":
#     main()
