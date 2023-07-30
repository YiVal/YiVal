from ..schemas.experiment_config import Experiment
from .selection_strategy import SelectionOutput, SelectionStrategy


class SelectionContext:

    def __init__(self, strategy: SelectionStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: SelectionStrategy):
        self._strategy = strategy

    def execute_selection(self, experiment: Experiment) -> SelectionOutput:
        return self._strategy.select(experiment)
