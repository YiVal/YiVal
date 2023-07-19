from typing import Optional

from .base_wrapper import BaseWrapper


class StringWrapper(BaseWrapper):
    """
    A wrapper for strings to manage experiment variations based on the global
    experiment state.
    If a variation for the given experiment name exists and the global ExperimentState
    is active,
    the variation will be used. Otherwise, it falls back to the original string.
    Attributes:
        _original_string (str): The original string value to be potentially replaced by
        a variation.
    Methods:
        __str__() -> str:
            Returns the variation if it exists and the global ExperimentState is active.
            Otherwise, returns the original string.
    """

    def __init__(self, original_string: str, name: str) -> None:
        super().__init__(name)
        self._original_string: str = original_string

    def __str__(self) -> str:
        variation: Optional[str] = self.get_variation()
        if variation:
            return variation
        return self._original_string
