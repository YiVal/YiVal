import hashlib
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List, Optional, Type

from ..schemas.common_structures import InputData
from ..schemas.data_generator_configs import BaseDataGeneratorConfig


class BaseDataGenerator(ABC):
    """
    Abstract base class for all data generators.
    """
    _registry: Dict[str, Dict[str, Any]] = {}
    default_config: Optional[BaseDataGeneratorConfig] = None

    @classmethod
    def get_data_generator(cls,
                           name: str) -> Optional[Type['BaseDataGenerator']]:
        """Retrieve data generator class from registry by its name."""
        return cls._registry.get(name, {}).get("class")

    @classmethod
    def get_default_config(cls,
                           name: str) -> Optional[BaseDataGeneratorConfig]:
        """Retrieve the default configuration of a data generator by its name."""
        return cls._registry.get(name, {}).get("default_config")

    def __init__(self, config: BaseDataGeneratorConfig):
        self.config = config

    @classmethod
    def get_config_class(cls,
                         name: str) -> Optional[Type[BaseDataGeneratorConfig]]:
        """Retrieve the configuration class of a generator_info by its name."""
        return cls._registry.get(name, {}).get("config_cls")

    @classmethod
    def register_data_generator(
        cls,
        name: str,
        data_generator_cls: Type['BaseDataGenerator'],
        config_cls: Optional[Type[BaseDataGeneratorConfig]] = None
    ):
        cls._registry[name] = {
            "class": data_generator_cls,
            "default_config": data_generator_cls.default_config,
            "config_cls": config_cls
        }

    @abstractmethod
    def generate_examples(self) -> Iterator[List[InputData]]:
        pass

    def generate_example_id(self, content: str) -> str:
        """
        Default function to generate an example_id for a given row of data.
        """
        return hashlib.md5(content.encode()).hexdigest()
