import importlib
import inspect
import os
import sys
import time
from collections import defaultdict
from importlib import import_module
from typing import Any, Dict, List

from ..combination_improvers.base_combination_improver import (
    BaseCombinationImprover,
)
from ..data.base_reader import BaseReader
from ..data_generators.base_data_generator import BaseDataGenerator
from ..evaluators.base_evaluator import BaseEvaluator
from ..evaluators.openai_elo_evaluator import OpenAIEloEvaluator
from ..logger.token_logger import TokenLogger
from ..result_selectors.selection_strategy import SelectionStrategy
from ..schemas.combination_improver_configs import (
    BaseCombinationImproverConfig,
)
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
from ..states.experiment_state import ExperimentState
from .evaluator import Evaluator


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
    }


def call_function_from_string(func_string: str, **kwargs) -> Any:
    """Call a function specified by a string."""
    function = import_function_from_string(func_string)
    return function(**kwargs)


def register_custom_readers(custom_readers: Dict[str, Dict[str, Any]]):
    for name, details in custom_readers.items():
        reader_cls_path = details["class"]
        module_name, class_name = reader_cls_path.rsplit(".", 1)
        reader_cls = getattr(import_module(module_name), class_name)

        config_cls = None
        if "config_cls" in details:
            config_cls_path = details["config_cls"]
            module_name, class_name = config_cls_path.rsplit(".", 1)
            config_cls = getattr(import_module(module_name), class_name)

        BaseReader.register_reader(name, reader_cls, config_cls)
    from ..data.csv_reader import CSVReader
    _ = CSVReader


def register_custom_improver(custom_improver: Dict[str, Dict[str, Any]]):
    for name, details in custom_improver.items():
        improver_cls_path = details["class"]
        module_name, class_name = improver_cls_path.rsplit(".", 1)
        improver_cls = getattr(import_module(module_name), class_name)

        config_cls = None
        if "config_cls" in details:
            config_cls_path = details["config_cls"]
            module_name, class_name = config_cls_path.rsplit(".", 1)
            config_cls = getattr(import_module(module_name), class_name)

        BaseCombinationImprover.register_combination_improver(
            name, improver_cls, config_cls
        )
    from ..combination_improvers.openai_prompt_based_combination_improver import (
        OpenAIPromptBasedCombinationImprover,
    )
    _ = OpenAIPromptBasedCombinationImprover


def register_custom_selection_strategy(
    custom_strategy: Dict[str, Dict[str, Any]]
):
    for name, details in custom_strategy.items():
        strategy_cls_path = details["class"]
        module_name, class_name = strategy_cls_path.rsplit(".", 1)
        strategy_cls = getattr(import_module(module_name), class_name)

        config_cls = None
        if "config_cls" in details:
            config_cls_path = details["config_cls"]
            module_name, class_name = config_cls_path.rsplit(".", 1)
            config_cls = getattr(import_module(module_name), class_name)

        SelectionStrategy.register_strategy(name, strategy_cls, config_cls)
    from ..result_selectors.ahp_selection import AHPSelection
    _ = AHPSelection


def register_custom_evaluators(custom_evaulators: Dict[str, Dict[str, Any]]):
    for name, details in custom_evaulators.items():
        evaluator_cls_path = details["class"]
        module_name, class_name = evaluator_cls_path.rsplit(".", 1)
        evaluator_cls = getattr(import_module(module_name), class_name)

        config_cls = None
        if "config_cls" in details:
            config_cls_path = details["config_cls"]
            module_name, class_name = config_cls_path.rsplit(".", 1)
            config_cls = getattr(import_module(module_name), class_name)

        BaseEvaluator.register_evaluator(name, evaluator_cls, config_cls)
    from ..evaluators.string_expected_result_evaluator import (
        StringExpectedResultEvaluator,
    )
    _ = StringExpectedResultEvaluator
    _ = OpenAIEloEvaluator


def register_custom_wrappers(custom_wrappers: Dict[str, Dict[str, Any]]):
    for name, details in custom_wrappers.items():
        wrapper_cls_path = details["class"]
        module_name, class_name = wrapper_cls_path.rsplit(".", 1)
        wrapper_cls = getattr(import_module(module_name), class_name)

        config_cls = None
        if "config_cls" in details:
            config_cls_path = details["config_cls"]
            module_name, class_name = config_cls_path.rsplit(".", 1)
            config_cls = getattr(import_module(module_name), class_name)

        BaseEvaluator.register_evaluator(name, wrapper_cls, config_cls)
    from ..wrappers.string_wrapper import StringWrapper
    _ = StringWrapper


def register_custom_data_generator(
    custom_data_generators: Dict[str, Dict[str, Any]]
):
    for name, details in custom_data_generators.items():
        data_generator_cls_path = details["class"]
        module_name, class_name = data_generator_cls_path.rsplit(".", 1)
        data_generator_cls = getattr(import_module(module_name), class_name)

        config_cls = None
        if "config_cls" in details:
            config_cls_path = details["config_cls"]
            module_name, class_name = config_cls_path.rsplit(".", 1)
            config_cls = getattr(import_module(module_name), class_name)

        BaseDataGenerator.register_data_generator(
            name, data_generator_cls, config_cls
        )
    from ..data_generators.openai_prompt_data_generator import (
        OpenAIPromptDataGenerator,
    )
    _ = OpenAIPromptDataGenerator


def register_variation_generator(
    custom_data_generators: Dict[str, Dict[str, Any]]
):
    for name, details in custom_data_generators.items():
        data_generator_cls_path = details["class"]
        module_name, class_name = data_generator_cls_path.rsplit(".", 1)
        data_generator_cls = getattr(import_module(module_name), class_name)

        config_cls = None
        if "config_cls" in details:
            config_cls_path = details["config_cls"]
            module_name, class_name = config_cls_path.rsplit(".", 1)
            config_cls = getattr(import_module(module_name), class_name)

        BaseDataGenerator.register_data_generator(
            name, data_generator_cls, config_cls
        )
    from ..data_generators.openai_prompt_data_generator import (
        OpenAIPromptDataGenerator,
    )
    _ = OpenAIPromptDataGenerator


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
    state: ExperimentState, logger: TokenLogger, evaluator: Evaluator
):
    results = []
    for combo in all_combinations:
        for name, variation in combo.items():
            state.set_specific_variation(name, variation)
            start_time = time.time()
            res = call_function_from_string(
                config["custom_function"],  # type: ignore
                **d.content
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


def get_improver(config: ExperimentConfig) -> BaseCombinationImprover | None:
    if "improver" not in config:  # type: ignore
        return None
    if config["improver"]:  # type: ignore
        improver_config = config["improver"]  # type: ignore
        improver_cls = BaseCombinationImprover.get_combination_improver(
            improver_config["name"]
        )
        if improver_cls:
            config_cls = BaseCombinationImprover.get_config_class(
                improver_config["name"]
            )
            if config_cls:
                if isinstance(improver_config, dict):
                    config_data = improver_config
                else:
                    config_data = improver_config.asdict()
                config_instance = config_cls(**config_data)
                improver_instance = improver_cls(config_instance)
                return improver_instance
            else:
                improver_instance = improver_cls(
                    BaseCombinationImproverConfig(name="")
                )
                return improver_instance
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
            grouped_experiment_result.evaluator_outputs = evaluator.evaluate_group_result(
                grouped_experiment_result.experiment_results
            )

    combo_metrics = defaultdict(list)
    for item in results:
        combo_metrics[str(item.combination)].append(item)

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
        group_experiment_results=grouped_experiment_results,
        combination_aggregated_metrics=cobo_aggregated_metrics
    )
    if evaluate_all:
        er = [experiment]
        evaluator.evaluate_based_on_all_results(er)
    return experiment
