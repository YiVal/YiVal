from typing import Any, Dict, Optional, Type

from ..schemas.wrapper_configs import BaseWrapperConfig
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
    _registry: Dict[str, Dict[str, Any]] = {}
    default_config: Optional[BaseWrapperConfig] = None

    @classmethod
    def register(cls, name: str):
        """Decorator to register new wrappers."""

        def inner(subclass: Type[BaseWrapper]):
            cls._registry[name] = {
                "class": subclass,
                "default_config": subclass.default_config
            }
            return subclass

        return inner

    def __init__(
        self, name: str, config: Optional[BaseWrapperConfig] = None
    ) -> None:
        self.name = name
        self.experiment_state = ExperimentState.get_instance()
        self.config = config

    def get_variation(self) -> Optional[Any]:
        if self.experiment_state.active:
            return self.experiment_state.get_next_variation(self.name)
        return None

    @classmethod
    def get_wrapper(cls, name: str) -> Optional[Type['BaseWrapper']]:
        """Retrieve wrapper class from registry by its name."""
        wrapper_info = cls._registry.get(name, {})
        return wrapper_info.get(
            "class", None
        ) if "class" in wrapper_info else None

    @classmethod
    def get_default_config(cls, name: str) -> Optional[BaseWrapperConfig]:
        """Retrieve the default configuration of a wrapper by its name."""
        wrapper_info = cls._registry.get(name, {})
        return wrapper_info.get(
            "default_config", None
        ) if "default_config" in wrapper_info else None

    @classmethod
    def get_config_class(cls, name: str) -> Optional[Type[BaseWrapperConfig]]:
        """Retrieve the configuration class of a reader by its name."""
        reader_info = cls._registry.get(name, {})
        return reader_info.get("config_cls", None)

    def get_active_config(self, name: str) -> Optional[BaseWrapperConfig]:
        if self.experiment_state.active and self.experiment_state.config.wrapper_configs:
            config = self.experiment_state.config.wrapper_configs.get(
                name, None
            )
            if config:
                config_cls = BaseWrapper.get_config_class(name)
                if config_cls:
                    return config_cls(**config.asdict())
        return None

    @classmethod
    def register_wrapper(
        cls,
        name: str,
        wrapper_cls: Type['BaseWrapper'],
        config_cls: Optional[Type[BaseWrapperConfig]] = None
    ):
        cls._registry[name] = {
            "class": wrapper_cls,
            "default_config": wrapper_cls.default_config,
            "config_cls": config_cls
        }
