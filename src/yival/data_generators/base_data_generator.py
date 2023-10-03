"""
This module provides a foundational architecture for programmatically
generating data.

Data generators are responsible for creating data programmatically based on
certain configurations.
The primary utility of these generators is in scenarios where synthetic or
mock data is required,
such as testing, simulations, and more. This module offers a base class that
outlines the primary
structure and functionalities of a data generator. It also provides methods to
register new
generators, retrieve existing ones, and fetch their configurations.
"""
import hashlib
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List, Optional, Type

from ..schemas.common_structures import InputData
from ..schemas.data_generator_configs import BaseDataGeneratorConfig


class BaseDataGenerator(ABC):
    """
    Abstract base class for all data generators.

    This class provides a blueprint for data generators and offers methods to
    register new generators,
    retrieve registered generators, and fetch their configurations.

    Attributes:
        _registry (Dict[str, Dict[str, Any]]): A registry to keep track of
                                                data generators.
        default_config (Optional[BaseDataGeneratorConfig]): Default
                                    configuration for the generator.
    """

    _registry: Dict[str, Dict[str, Any]] = {}
    default_config: Optional[BaseDataGeneratorConfig] = None

    @staticmethod
    def input_data_to_csv_row(data: InputData) -> Dict[str, Any]:
        row = {
            'example_id': data.example_id,
        }
        for key, value in data.content.items():
            row[key] = value
        return row

    @classmethod
    def get_data_generator(cls,
                           name: str) -> Optional[Type['BaseDataGenerator']]:
        """Retrieve data generator class from registry by its name."""
        return cls._registry.get(name, {}).get("class")

    @classmethod
    def get_default_config(cls,
                           name: str) -> Optional[BaseDataGeneratorConfig]:
        """Retrieve the default configuration of a data generator by its
        name."""
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
        """
        Register data generator class with the registry.
        """
        cls._registry[name] = {
            "class": data_generator_cls,
            "default_config": data_generator_cls.default_config,
            "config_cls": config_cls
        }

    @abstractmethod
    def generate_examples(self) -> Iterator[List[InputData]]:
        """
        Generate data examples and return an iterator of lists containing
        InputData.
        
        This method is designed to produce data programmatically. The number
        and nature of data examples are determined by the generator's
        configuration.

        Returns:
            Iterator[List[InputData]]: An iterator yielding lists of InputData
            objects.
        """

    def generate_example_id(self, content: str) -> str:
        """
        Generate a unique identifier for a given content string.

        Args:
            content (str): The content for which an ID should be generated.

        Returns:
            str: A unique MD5 hash derived from the content.
        """
        return hashlib.md5(content.encode()).hexdigest()
