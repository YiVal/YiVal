from typing import Any, Dict, Optional

from ..schemas.wrapper_configs import StringWrapperConfig
from ..states.experiment_state import ExperimentState
from .base_wrapper import BaseWrapper


class StringWrapper(BaseWrapper):
    """
    A wrapper for strings to manage experiment variations based on the
    experiment state. If a variation for the given experiment name exists and 
    the ExperimentState is active, the variation is used. Otherwise, 
    the original string is returned.
    """
    default_config = StringWrapperConfig()

    def __init__(
        self,
        template: str,
        name: str,
        variables: Dict[str, Any] = {},
        config: Optional[StringWrapperConfig] = None,
        state: Optional[ExperimentState] = None,
    ) -> None:
        super().__init__(name, config, state)
        self._template = template
        self._variables = variables

    def __str__(self) -> str:
        variation = self.get_variation()
        if variation is None:
            variation = self._template
        try:
            return variation.format(**self._variables)
        except KeyError:
            return variation


BaseWrapper.register_wrapper(
    "string_wrapper", StringWrapper, StringWrapperConfig
)
