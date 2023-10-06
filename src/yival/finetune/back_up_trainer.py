"""
This module is the back up trainer

It will only be called when the dependency is not imported correctly
"""

from ..experiment.evaluator import Evaluator
from ..logger.token_logger import TokenLogger
from ..schemas.experiment_config import Experiment, ExperimentConfig, TrainerOutput
from .base_trainer import BaseTrainer


class BackUpTrainer(BaseTrainer):

    def train(
        self, experiment: Experiment, config: ExperimentConfig,
        evaluator: Evaluator, token_logger: TokenLogger
    ) -> TrainerOutput:
        raise ImportError(
            "Trainer was not successfully imported. Please check your dependencies."
        )