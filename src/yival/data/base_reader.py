"""
This module provides an abstract foundation for data readers.

Data readers are responsible for reading data from various sources, and this
module offers a base class to define and register new readers, retrieve
existing ones, and fetch their configurations. The design encourages efficient
parallel processing by reading data in chunks.
"""
import hashlib
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List, Optional, Type

from ..schemas.common_structures import InputData
from ..schemas.reader_configs import BaseReaderConfig


class BaseReader(ABC):
    """
    Abstract base class for all data readers.

    This class provides a blueprint for data readers and offers methods to
    register new readers,
    retrieve registered readers, and fetch their configurations.

    Attributes:
        _registry (Dict[str, Dict[str, Any]]): A registry to keep track of
                                                data readers.
        default_config (Optional[BaseReaderConfig]): Default configuration for
                                                    the reader.
    """
    _registry: Dict[str, Dict[str, Any]] = {}
    default_config: Optional[BaseReaderConfig] = None

    @classmethod
    def register(
        cls, name: str, config_cls: Optional[Type[BaseReaderConfig]] = None
    ):
        """Decorator to register new readers."""

        def inner(subclass: Type[BaseReader]):
            cls._registry[name] = {
                "class": subclass,
                "default_config": subclass.default_config,
                "config_cls": config_cls
            }
            return subclass

        return inner

    @classmethod
    def get_reader(cls, name: str) -> Optional[Type['BaseReader']]:
        """Retrieve reader class from registry by its name."""
        reader_info = cls._registry.get(name, {})
        return reader_info.get(
            "class", None
        ) if "class" in reader_info else None

    @classmethod
    def get_default_config(cls, name: str) -> Optional[BaseReaderConfig]:
        """Retrieve the default configuration of a reader by its name."""
        reader_info = cls._registry.get(name, {})
        return reader_info.get(
            "default_config", None
        ) if "default_config" in reader_info else None

    def __init__(self, config: BaseReaderConfig):
        self.config = config

    @classmethod
    def get_config_class(cls, name: str) -> Optional[Type[BaseReaderConfig]]:
        """Retrieve the configuration class of a reader by its name."""
        reader_info = cls._registry.get(name, {})
        return reader_info.get("config_cls", None)

    @classmethod
    def register_reader(
        cls,
        name: str,
        reader_cls: Type['BaseReader'],
        config_cls: Optional[Type[BaseReaderConfig]] = None
    ):
        """
        Register reader's subclass along with its default configuration and
        config class.
        """
        cls._registry[name] = {
            "class": reader_cls,
            "default_config": reader_cls.default_config,
            "config_cls": config_cls
        }

    @abstractmethod
    def read(self, path: str) -> Iterator[List[InputData]]:
        """
        Read data from the given file path and return an iterator of lists
        containing InputData.

        This method is designed to read data in chunks for efficient parallel
        processing. The chunk size is determined by the reader's configuration.

        Args:
            path (str): The path to the file containing data to be read.

        Returns:
            Iterator[List[InputData]]: An iterator yielding lists of InputData
            objects.
        """

    def generate_example_id(self, row_data: Dict[str, Any], path: str) -> str:
        """
        Default function to generate an example_id for a given row of data.
        """
        row_hash = hashlib.md5(str(row_data).encode()).hexdigest()
        return f"{path}_{row_hash}"
