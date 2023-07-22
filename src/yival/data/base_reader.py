from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List

from ..schemas.reader_configs import BaseReaderConfig


class BaseReader(ABC):
    """
    Abstract base class for all data readers.
    """

    def __init__(self, config: BaseReaderConfig):
        self.config = config

    @abstractmethod
    def read(self, path: str) -> Iterator[List[Dict[str, Any]]]:
        pass
