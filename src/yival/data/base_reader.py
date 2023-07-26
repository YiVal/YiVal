import hashlib
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List, Optional, Type

from ..schemas.common_structures import InputData
from ..schemas.reader_configs import BaseReaderConfig


class BaseReader(ABC):
    """
    Abstract base class for all data readers.
    """
    _registry: Dict[str, Dict[str, Any]] = {}
    default_config: Optional[BaseReaderConfig] = None

    @classmethod
    def register(cls, name: str):
        """Decorator to register new readers."""

        def inner(subclass: Type[BaseReader]):
            cls._registry[name] = {
                "class": subclass,
                "default_config": subclass.default_config
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

    @abstractmethod
    def read(self, path: str) -> Iterator[List[InputData]]:
        pass

    def generate_example_id(self, row_data: Dict[str, Any], path: str) -> str:
        """
        Default function to generate an example_id for a given row of data.
        """
        row_hash = hashlib.md5(str(row_data).encode()).hexdigest()
        return f"{path}_{row_hash}"
