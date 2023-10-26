import asyncio
import importlib
import inspect
import json
import os
import sys
import time
from collections import defaultdict
from importlib import import_module
from typing import Any, Dict, List

from yival.variation_generators.chain_of_density_prompt import ChainOfDensityPromptGenerator

from ..data.base_reader import BaseReader
from ..data.csv_reader import CSVReader
from ..data.huggingface_dataset_reader import HuggingFaceDatasetReader
from ..data_generators.base_data_generator import BaseDataGenerator
from ..enhancers.base_combination_enhancer import BaseCombinationEnhancer
from ..evaluators.alpaca_eval_evaluator import AlpacaEvalEvaluator
from ..evaluators.base_evaluator import BaseEvaluator
from ..evaluators.bertscore_evaluator import BertScoreEvaluator
from ..evaluators.openai_elo_evaluator import OpenAIEloEvaluator
from ..evaluators.openai_prompt_based_evaluator import OpenAIPromptBasedEvaluator
from ..evaluators.python_validation_evaluator import PythonValidationEvaluator
from ..evaluators.rouge_evaluator import RougeEvaluator
from ..evaluators.string_expected_result_evaluator import StringExpectedResultEvaluator
from ..finetune.base_trainer import BaseTrainer
from ..logger.token_logger import TokenLogger
from ..result_selectors.ahp_selection import AHPSelection
from ..result_selectors.selection_strategy import SelectionStrategy
from ..schemas.combination_enhancer_configs import BaseCombinationEnhancerConfig
from ..schemas.evaluator_config import MethodCalculationMethod
from ..schemas.experiment_config import (
    CombinationAggregatedMetrics,
    Experiment,
    ExperimentConfig,
    ExperimentResult,
    GroupedExperimentResult,
    InputData,
    Metric,
)
from ..schemas.selector_strategies import BaseConfig
from ..schemas.trainer_configs import BaseTrainerConfig
from ..states.experiment_state import ExperimentState
from ..variation_generators.base_variation_generator import BaseVariationGenerator
from ..variation_generators.openai_prompt_based_variation_generator import (
    OpenAIPromptBasedVariationGenerator,
)
from ..wrappers.base_wrapper import BaseWrapper
from ..wrappers.string_wrapper import StringWrapper
from .evaluator import Evaluator


def is_async_function(func):
    return asyncio.iscoroutinefunction(func)


def import_function_from_string(func_string: str):
    """Helper function to import a function from a string."""
    try:
        # Direct import for built-in functions
        module_name, function_name = func_string.rsplit('.', 1)
        module = importlib.import_module(module_name)
    except ImportError:
        # Dynamic import for user-specified functions
        module_path, module_name, function_name = func_string.rsplit('.', 2)
        sys.path.append(os.path.abspath(module_path))
        module = importlib.import_module(module_name)

    function = getattr(module, function_name)
    return function


def get_function_args(func_string: str):
    """Get argument types of a function."""
    function = import_function_from_string(func_string)
    signature = inspect.signature(function)
    return {
        name: str(param.annotation)
        for name, param in signature.parameters.items()
        if name.lower() != "state"
    }


def call_function_from_string(func_string: str, **kwargs) -> Any:
    """Call a function specified by a string."""
    function = import_function_from_string(func_string)
    return function(**kwargs)


async def acall_function_from_string(func_string: str, **kwargs) -> Any:

    function = import_function_from_string(func_string)
    if is_async_function(function):
        return await function(**kwargs)
    else:
        return function(**kwargs)


def _add_to_sys_path_if_not_present(directory: str):
    """Add directory to sys.path if not already present."""
    if directory not in sys.path:
        sys.path.append(directory)


def _get_class_from_path(cls_path: str):
    """Retrieve a class from a module using its full path."""
    module_path, class_name = cls_path.rsplit(".", 1)
    directory, base_module_name = os.path.split(module_path)

    _add_to_sys_path_if_not_present(directory)
    return getattr(import_module(base_module_name), class_name)


def register_custom_readers(custom_readers: Dict[str, Dict[str, Any]]):
    for name, details in custom_readers.items():
        reader_cls = _get_class_from_path(details["class"])

        config_cls = None
        if "config_cls" in details:
            config_cls = _get_class_from_path(details["config_cls"])

        BaseReader.register_reader(name, reader_cls, config_cls)

    _ = CSVReader
    _ = HuggingFaceDatasetReader


def register_custom_enhancer(custom_enhancer: Dict[str, Dict[str, Any]]):
    for name, details in custom_enhancer.items():
        enhancer_cls = _get_class_from_path(details["class"])

        config_cls = None
        if "config_cls" in details:
            config_cls = _get_class_from_path(details["config_cls"])

        BaseCombinationEnhancer.register_enhancer(
            name, enhancer_cls, config_cls
        )
    from ..enhancers.openai_prompt_based_combination_enhancer import (
        OpenAIPromptBasedCombinationEnhancer,
    )
    _ = OpenAIPromptBasedCombinationEnhancer


def register_custom_selection_strategy(
    custom_strategy: Dict[str, Dict[str, Any]]
):
    for name, details in custom_strategy.items():
        strategy_cls = _get_class_from_path(details["class"])

        config_cls = None
        if "config_cls" in details:
            config_cls = _get_class_from_path(details["config_cls"])

        SelectionStrategy.register_strategy(name, strategy_cls, config_cls)
    _ = AHPSelection


def register_custom_evaluators(custom_evaulators: Dict[str, Dict[str, Any]]):
    for name, details in custom_evaulators.items():
        evaluator_cls = _get_class_from_path(details["class"])

        config_cls = None
        if "config_cls" in details:
            config_cls = _get_class_from_path(details["config_cls"])

        BaseEvaluator.register_evaluator(name, evaluator_cls, config_cls)
    _ = StringExpectedResultEvaluator
    _ = OpenAIEloEvaluator
    _ = PythonValidationEvaluator
    _ = AlpacaEvalEvaluator
    _ = BertScoreEvaluator
    _ = OpenAIPromptBasedEvaluator
    _ = RougeEvaluator


def register_custom_wrappers(custom_wrappers: Dict[str, Dict[str, Any]]):
    for name, details in custom_wrappers.items():
        wrapper_cls = _get_class_from_path(details["class"])

        config_cls = None
        if "config_cls" in details:
            config_cls = _get_class_from_path(details["config_cls"])

        BaseWrapper.register_wrapper(name, wrapper_cls, config_cls)

    _ = StringWrapper


def register_custom_data_generator(
    custom_data_generators: Dict[str, Dict[str, Any]]
):
    for name, details in custom_data_generators.items():
        data_generator_cls = _get_class_from_path(details["class"])

        config_cls = None
        if "config_cls" in details:
            config_cls = _get_class_from_path(details["config_cls"])

        BaseDataGenerator.register_data_generator(
            name, data_generator_cls, config_cls
        )
    from ..data_generators.openai_prompt_data_generator import OpenAIPromptDataGenerator
    _ = OpenAIPromptDataGenerator


def register_custom_variation_generators(
    custom_variation_generators: Dict[str, Dict[str, Any]]
):
    for name, details in custom_variation_generators.items():
        variation_generator_cls = _get_class_from_path(details["class"])

        config_cls = None
        if "config_cls" in details:
            config_cls = _get_class_from_path(details["config_cls"])

        BaseVariationGenerator.register_variation_generator(
            name, variation_generator_cls, config_cls
        )
    _ = OpenAIPromptBasedVariationGenerator
    _ = ChainOfDensityPromptGenerator


def calculate_metrics(
    results: List[ExperimentResult]
) -> Dict[str, List[Metric]]:
    if not results:
        return {}

    res: Dict[str, List[Metric]] = defaultdict(list)

    # Assuming the metrics method across all results are the same,
    # so we'll use results[0] just to get a reference to the metric_calculators
    reference_evaluator_outputs = results[0].evaluator_outputs
    if reference_evaluator_outputs:
        for evaluator_output in reference_evaluator_outputs:
            for metric_calculator in evaluator_output.metric_calculators:
                if metric_calculator[
                    "method"
                ] == MethodCalculationMethod.AVERAGE.value:  # type: ignore
                    # Calculate average across all results
                    total = sum(
                        eo.result for r in results if r.evaluator_outputs
                        for eo in r.evaluator_outputs
                        if eo.name == evaluator_output.name
                        and eo.display_name == evaluator_output.display_name
                    )
                    average_value = total / len(results)
                    key = evaluator_output.name
                    key += ": " + evaluator_output.display_name if evaluator_output.display_name else ""
                    res[key].append(
                        Metric(
                            name=MethodCalculationMethod.AVERAGE.value,
                            value=average_value
                        )
                    )

    return res


def calculate_average_token(results: List[ExperimentResult]) -> float:
    if not results:
        return 0

    total = sum(r.token_usage for r in results)
    return total / len(results)


def calculate_average_latency(results: List[ExperimentResult]) -> float:
    if not results:
        return 0

    total = sum(r.latency for r in results)
    return total / len(results)


def run_single_input(
    d: InputData, config: ExperimentConfig, all_combinations: List[Dict[str,
                                                                        Any]],
    logger: TokenLogger, evaluator: Evaluator
):
    results = []
    tmp_state = ExperimentState()
    tmp_state.active = True
    for combo in all_combinations:
        for name, variation in combo.items():
            tmp_state.set_specific_variation(name, variation)
        start_time = time.time()
        res = call_function_from_string(
            config["custom_function"],  # type: ignore
            **d.content,
            state=tmp_state
        ) if "custom_function" in config else None  #type: ignore

        end_time = time.time()
        latency = end_time - start_time  # Time in seconds

        tokens_used = logger.get_current_usage()
        result = ExperimentResult(
            input_data=d,
            combination=combo,
            raw_output=res,
            latency=latency,
            token_usage=tokens_used,
            evaluator_outputs=[]
        )
        if result.evaluator_outputs is not None:
            result.evaluator_outputs.extend(
                evaluator.evaluate_individual_result(result)
            )
        results.append(result)
    return results


async def arun_single_input(
    d: InputData, config: ExperimentConfig, all_combinations: List[Dict[str,
                                                                        Any]],
    logger: TokenLogger, evaluator: Evaluator
):
    results = []
    tmp_state = ExperimentState()
    tmp_state.active = True
    for combo in all_combinations:
        for name, variation in combo.items():
            tmp_state.set_specific_variation(name, variation)
        start_time = time.time()
        res = await acall_function_from_string(
            config["custom_function"],  # type: ignore
            **d.content,
            state=tmp_state
        )
        end_time = time.time()
        latency = end_time - start_time  # Time in seconds

        tokens_used = logger.get_current_usage()
        result = ExperimentResult(
            input_data=d,
            combination=combo,
            raw_output=res,
            latency=latency,
            token_usage=tokens_used,
            evaluator_outputs=[]
        )
        if result.evaluator_outputs is not None:
            result.evaluator_outputs.extend(
                evaluator.evaluate_individual_result(result)
            )
        results.append(result)
    return results


def get_selection_strategy(
    config: ExperimentConfig
) -> SelectionStrategy | None:
    if "selection_strategy" not in config:  # type: ignore
        return None
    if config["selection_strategy"]:  # type: ignore
        for strategy, strategy_config in config["selection_strategy"
                                                ].items(  # type: ignore
                                                ):
            strategy_cls = SelectionStrategy.get_strategy(strategy)
            if strategy_cls:
                config_cls = SelectionStrategy.get_config_class(strategy)
                if config_cls:
                    if isinstance(strategy_config, dict):
                        config_data = strategy_config
                    else:
                        config_data = strategy_config.asdict()
                    config_instance = config_cls(**config_data)
                    strategy_instance = strategy_cls(config_instance)
                else:
                    strategy_instance = strategy_cls(BaseConfig())

                return strategy_instance
    return None


def get_enhancer(config: ExperimentConfig) -> BaseCombinationEnhancer | None:
    if "enhancer" not in config:  # type: ignore
        return None
    if config["enhancer"]:  # type: ignore
        enhancer_config = config["enhancer"]  # type: ignore
        enhancer_cls = BaseCombinationEnhancer.get_enhancer(
            enhancer_config["name"]
        )
        if enhancer_cls:
            config_cls = BaseCombinationEnhancer.get_config_class(
                enhancer_config["name"]
            )
            if config_cls:
                if isinstance(enhancer_config, dict):
                    config_data = enhancer_config
                else:
                    config_data = enhancer_config.asdict()
                config_instance = config_cls(**config_data)
                enhancer_instance = enhancer_cls(config_instance)
                return enhancer_instance
            else:
                enhancer_instance = enhancer_cls(
                    BaseCombinationEnhancerConfig(name="")
                )
                return enhancer_instance
    return None


def remove_none_values(d):
    if isinstance(d, dict):
        return {
            k: remove_none_values(v)
            for k, v in d.items() if v is not None
        }
    else:
        return d


def get_trainer(config: ExperimentConfig) -> BaseTrainer | None:
    if "trainer" not in config:  #type: ignore
        return None
    if config["trainer"]:  #type: ignore
        trainer_config = config["trainer"]  #type: ignore
        trainer_cls = BaseTrainer.get_trainer(trainer_config["name"])
        if trainer_cls:
            config_cls = BaseTrainer.get_config_class(trainer_config["name"])
            default_config = BaseTrainer.get_default_config(
                trainer_config["name"]
            )
            if config_cls:
                if isinstance(trainer_config, dict):
                    config_data = trainer_config
                else:
                    config_data = trainer_config.asdict()
                #remove None value
                config_data = remove_none_values(config_data)
                #update data use default_config
                default_config = default_config.asdict()  #type: ignore
                default_config.update(config_data)  #type: ignore
                config_instance = config_cls(**default_config)  #type: ignore
                trainer_instance = trainer_cls(config_instance)  #type: ignore
                return trainer_instance
            else:
                trainer_instance = trainer_cls(BaseTrainerConfig(name=""))
                return trainer_instance
    return None


def generate_experiment(
    results: List[ExperimentResult],
    evaluator: Evaluator,
    evaluate_all: bool = True,
    evaluate_group: bool = True
) -> Experiment:
    grouped_experiment_results: List[GroupedExperimentResult] = defaultdict(
        list
    )  # type: ignore

    for item in results:
        key = str(item.input_data)
        grouped_experiment_results[key].append(item)  # type: ignore
    grouped_experiment_results = [
        GroupedExperimentResult(group_key=k, experiment_results=v)
        for k, v in grouped_experiment_results.items()  # type: ignore
    ]
    if evaluate_group:
        for grouped_experiment_result in grouped_experiment_results:
            evaluator.evaluate_group_result(
                grouped_experiment_result.experiment_results
            )

    enable_custom_func = False
    if results[0].raw_output:
        enable_custom_func = True

    combo_metrics = defaultdict(list)
    for item in results:
        combo_str = json.dumps(item.combination)
        combo_metrics[combo_str].append(item)

    cobo_aggregated_metrics = [
        CombinationAggregatedMetrics(
            combo_key=k, experiment_results=v, aggregated_metrics={}
        ) for k, v in combo_metrics.items()
    ]

    for cobo_aggregated_metric in cobo_aggregated_metrics:
        cobo_aggregated_metric.aggregated_metrics = calculate_metrics(
            cobo_aggregated_metric.experiment_results
        )
        cobo_aggregated_metric.average_token_usage = calculate_average_token(
            cobo_aggregated_metric.experiment_results
        )
        cobo_aggregated_metric.average_latency = calculate_average_latency(
            cobo_aggregated_metric.experiment_results
        )

    experiment = Experiment(
        enable_custom_func=enable_custom_func,
        group_experiment_results=grouped_experiment_results,
        combination_aggregated_metrics=cobo_aggregated_metrics
    )

    if evaluate_all:
        er = [experiment]
        evaluator.evaluate_based_on_all_results(er)
    return experiment
