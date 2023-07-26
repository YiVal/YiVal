from typing import Optional

from ..schemas.wrapper_configs import StringWrapperConfig
from .base_wrapper import BaseWrapper


@BaseWrapper.register("string_wrapper")
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

    def __init__(
        self,
        original_string: str,
        name: str,
        config: Optional[StringWrapperConfig] = None
    ) -> None:
        super().__init__(name, config)
        self._original_string: str = original_string

    def __str__(self) -> str:
        variation: Optional[str] = self.get_variation()
        if variation:
            return variation
        return self._original_string
