from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List

from tqdm import tqdm

from ..logger.token_logger import TokenLogger
from ..result_selectors.selection_context import SelectionContext
from ..schemas.common_structures import InputData
from ..schemas.experiment_config import (
    Experiment,
    ExperimentConfig,
    ExperimentResult,
    WrapperConfig,
    WrapperVariation,
)
from ..states.experiment_state import ExperimentState
from .evaluator import Evaluator
from .rate_limiter import RateLimiter
from .utils import (
    generate_experiment,
    get_selection_strategy,
    register_custom_data_generator,
    register_custom_enhancer,
    register_custom_evaluators,
    register_custom_selection_strategy,
    register_custom_variation_generators,
    register_custom_wrappers,
    run_single_input,
)


class LiteExperimentRunner:
    """
    LiteExperimentRunner  
    
    This runner is designed for situation you already have assemble all datas & evaluators...
    And just want to get experiment results on given data

    And you can easily update all variations through /update_variations()/  

    :)

    """

    def __init__(
        self, config: ExperimentConfig, limiter: RateLimiter,
        data: List[InputData], token_logger: TokenLogger, evaluator: Evaluator
    ):
        self.config = config
        self.limiter = limiter
        self.data = data
        self.token_logger = token_logger
        self.evaluator = evaluator

    def _register_custom_components(self):
        """
        Register custom components based on the configureation.

        If run lite experiment runner , this step is necessary
        """
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

    def parallel_task(self, data, all_combinations, logger, evaluator):
        """
        Execute a single input run in parallel
        """
        self.limiter()
        return run_single_input(
            data, self.config, all_combinations, logger, evaluator
        )

    def set_variations(self, variations: List[Dict[str, List[str]]]):
        """
        set all variations for current experiment
        variations are format in 
        [
            {
                var1_name: ["a","b","c"]
            },
            {
                var2_name: ["d","e","f"]
            }
        ]
        """
        self.config["variations"] = []  #type: ignore
        for variation_dict in variations:
            for name, values in variation_dict.items():
                wrapper_variations = [
                    WrapperVariation(
                        value=v, value_type=str(type(v)).split("'")[1]
                    ) for v in values
                ]
                self.config["variations"].append(   #type: ignore
                    (WrapperConfig(name=name, variations=wrapper_variations))
                )

    def run_experiment(self, enable_selector: bool) -> Experiment:
        self._register_custom_components()
        state = ExperimentState.get_instance()
        state = ExperimentState.get_instance()
        state.clear_variations_for_experiment()
        state.set_experiment_config(self.config)
        state.active = True
        all_combinations = state.get_all_variation_combinations()

        experiment_results: List[ExperimentResult] = []

        total = len(self.data)

        with tqdm(
            total=total,
            desc="[lite_experiment_runner] Processing",
            unit="item"
        ) as pbar:
            with ThreadPoolExecutor() as executor:
                for res in executor.map(
                    self.parallel_task, self.data,
                    [all_combinations] * len(self.data),
                    [self.token_logger] * len(self.data),
                    [self.evaluator] * len(self.data)
                ):
                    experiment_results.extend(res)
                    pbar.update(len(res))

        experiment = generate_experiment(
            experiment_results,
            self.evaluator,
            evaluate_group=False,
            evaluate_all=False
        )

        if enable_selector:
            strategy = get_selection_strategy(self.config)
            if strategy:
                context_trade_off = SelectionContext(strategy)
                experiment.selection_output = context_trade_off.execute_selection( # type: ignore
                    experiment=experiment
                )

        return experiment