import hashlib
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List

from ..schemas.common_structures import InputData
from ..schemas.reader_configs import BaseReaderConfig


class BaseReader(ABC):
    """
    Abstract base class for all data readers.
    """

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
