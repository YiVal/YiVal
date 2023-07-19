from typing import Any, Optional

from ..states.experiment_state import ExperimentState


class BaseWrapper:
    """
    Base wrapper class for managing experiment variations based on the global
    experiment state.

    This class acts as an interface to manage and retrieve variations associated
    with a given experiment name. If the global ExperimentState is active, it retrieves
    the next variation for the associated experiment name. If the ExperimentState is not
    active or no variation is found, it returns None.

    Attributes:
        name (str): The name of the experiment associated with this wrapper instance.

    Methods:
        get_variation() -> Optional[Any]:
            Depending on the global ExperimentState's activity status, retrieves the
            next variation for the associated experiment name. If the state is inactive
            or no variations are found, returns None.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.experiment_state = ExperimentState.get_instance()

    def get_variation(self) -> Optional[Any]:
        if self.experiment_state.active:
            return self.experiment_state.get_next_variation(self.name)
        return None
