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
        get_variation() -> Optional[str]:
            Depending on the global ExperimentState's activity status, retrieves the
            next variation for the associated experiment name. If the state is inactive
            or no variations are found, returns None.
    """

    def __init__(self, name):
        """
        Initializes a new BaseWrapper instance with the provided experiment name.

        Args:
            name (str): The name of the experiment associated with this wrapper.
        """
        self.name = name

    def get_variation(self):
        """
        Fetches the next variation for the associated experiment name based on the
        global ExperimentState.

        If the global ExperimentState is active, this method retrieves the next
        variation for the associated experiment name. If the ExperimentState
        is inactive or no variations are found, it returns None.

        Returns:
            Optional[str]: The next variation for the experiment name if available and
            state is active.
            Otherwise, returns None.
        """
        if ExperimentState().active:
            return ExperimentState().get_next_variation(self.name)
        return None
