"""
This module is the back up trainer

It will only be called when the dependency is not imported correctly
"""

from ..schemas.experiment_config import Experiment, ExperimentConfig, TrainerOutput
from .base_trainer import BaseTrainer


class BackUpTrainer(BaseTrainer):

    def train(
        self,
        experiment: Experiment,
        config: ExperimentConfig,
    ) -> TrainerOutput:
        raise ImportError(
            "Trainer was not successfully imported. Please check your dependencies."
        )