# common_structures.py
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional


@dataclass
class InputData:
    """
    Represents the input data for an experiment example.

    Attributes:
    - example_id (str): A unique identifier for the example.
    - content (Dict[str, Any]): A dictionary that contains all the necessary input
      parameters for the custom function.
    - expected_result (Optional[Any]): The expected result given the input.
    """

    example_id: str
    content: Dict[str, Any]
    expected_result: Optional[Any] = None

    def asdict(self):
        return asdict(self)