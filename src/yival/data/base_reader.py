from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List


class BaseReader(ABC):
    """
    Abstract base class for all data readers.
    """

    @abstractmethod
    def read(self, path: str, chunk_size: int) -> Iterator[List[Dict[str, Any]]]:
        pass
