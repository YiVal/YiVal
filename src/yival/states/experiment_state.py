from collections import defaultdict
from typing import Any, Dict, List, Optional


class ExperimentState:
    """
    Represents the state for managing experiment variations.

    This class maintains the state of active experiments and their variations. 

    Attributes:
        active (bool): Indicates if the experiment is currently active.
        current_variations (Dict[str, List[Any]]): A dictionary where keys are
        experiment names and values are lists of variations.
        counters (Dict[str, int]): A counter for each experiment name to rotate through
        its variations.

    Methods:
        get_next_variation(name: str) -> Optional[Any]:
            Depending on the global ExperimentState's activity status, retrieves the
            next variation for the associated experiment name. If the state is inactive
            or no variations are found, returns None.
    """

    _shared_instance = None

    @staticmethod
    def get_instance():
        if ExperimentState._shared_instance is None:
            ExperimentState._shared_instance = ExperimentState()
        return ExperimentState._shared_instance

    def __init__(self) -> None:
        self.active: bool = False
        self.current_variations: Dict[str, List[Any]] = {}
        self.counters: Dict[str, int] = defaultdict(int)

    def get_next_variation(self, name: str) -> Optional[Any]:
        variations = self.current_variations.get(name, [])
        if self.counters[name] < len(variations):
            variation = variations[self.counters[name]]
            self.counters[name] += 1
            return variation
        return None

    def set_variations_for_experiment(
        self, name: str, variations: List[Any]
    ) -> None:
        self.current_variations[name] = variations
