from concurrent.futures import ThreadPoolExecutor
from typing import List, Union

from ..evaluators.base_evaluator import BaseEvaluator
from ..schemas.evaluator_config import (
    ComparisonEvaluatorConfig,
    EvaluatorConfig,
    EvaluatorOutput,
    EvaluatorType,
    GlobalEvaluatorConfig,
)
from ..schemas.experiment_config import Experiment, ExperimentResult


def evaluate_config(config, result):
    if not isinstance(config, dict):
        config_dict = config.asdict()
    else:
        config_dict = config

    if config_dict["evaluator_type"] == EvaluatorType.INDIVIDUAL.value:
        evaluator_cls = BaseEvaluator.get_evaluator(config_dict["name"])
        if evaluator_cls:
            config_cls = BaseEvaluator.get_config_class(config_dict["name"])
            if config_cls:
                if isinstance(config_dict, dict):
                    config_data = config_dict
                else:
                    config_data = config_dict.asdict()
                config_instance = config_cls(**config_data)
                evaluator = evaluator_cls(config_instance)
                return evaluator.evaluate(result)
    return None


class Evaluator:
    """
    Utility class to evaluate ExperimentResult.
    """

    def __init__(
        self, configs: List[Union[EvaluatorConfig, ComparisonEvaluatorConfig,
                                  GlobalEvaluatorConfig]]
    ):
        self.configs = configs

    def evaluate_individual_result(
        self, result: ExperimentResult
    ) -> List[EvaluatorOutput]:
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(evaluate_config, config, result)
                for config in self.configs
            ]

        # Gather results, filter out None results
        return [
            future.result() for future in futures
            if future.result() is not None
        ]

    # def evaluate_individual_result(
    #     self, result: ExperimentResult
    # ) -> List[EvaluatorOutput]:
    #     res = []
    #     for config in self.configs:
    #         if not isinstance(config, dict):
    #             config_dict = config.asdict()
    #         else:
    #             config_dict = config
    #         if config_dict["evaluator_type"] == EvaluatorType.INDIVIDUAL.value:
    #             evaluator_cls = BaseEvaluator.get_evaluator(
    #                 config_dict["name"]
    #             )
    #             if evaluator_cls:
    #                 config_cls = BaseEvaluator.get_config_class(
    #                     config_dict["name"]
    #                 )
    #                 if config_cls:
    #                     if isinstance(config_dict, dict):
    #                         config_data = config_dict
    #                     else:
    #                         config_data = config_dict.asdict()
    #                     config_instance = config_cls(**config_data)
    #                     evaluator = evaluator_cls(config_instance)
    #                     res.append(evaluator.evaluate(result))

    #     return res

    def evaluate_group_result(self, results: List[ExperimentResult]) -> None:
        for config in self.configs:
            if not isinstance(config, dict):
                config_dict = config.asdict()
            else:
                config_dict = config
            if config_dict["evaluator_type"] == EvaluatorType.COMPARISON.value:
                evaluator_cls = BaseEvaluator.get_evaluator(
                    config_dict["name"]
                )
                if evaluator_cls:
                    config_cls = BaseEvaluator.get_config_class(
                        config_dict["name"]
                    )
                    if config_cls:
                        if isinstance(config_dict, dict):
                            config_data = config_dict
                        else:
                            config_data = config_dict.asdict()
                        config_instance = config_cls(**config_data)
                        evaluator = evaluator_cls(config_instance)
                        evaluator.evaluate_comparison(results)

    def evaluate_based_on_all_results(
        self, experiment: List[Experiment]
    ) -> None:

        for config in self.configs:
            config_dict = config.asdict(
            ) if not isinstance(config, dict) else config
            if config_dict["evaluator_type"] == EvaluatorType.ALL.value:

                evaluator_cls = BaseEvaluator.get_evaluator(
                    config_dict["name"]
                )

                if evaluator_cls:
                    config_cls = BaseEvaluator.get_config_class(
                        config_dict["name"]
                    )
                    if config_cls:
                        if isinstance(config_dict, dict):
                            config_data = config_dict
                        else:
                            config_data = config_dict.asdict()

                        config_instance = config_cls(**config_data)
                        evaluator = evaluator_cls(config_instance)

                        evaluator.evaluate_based_on_all_results(experiment)
