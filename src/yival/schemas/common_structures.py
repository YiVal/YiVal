# common_structures.py
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class InputData:
    """
    Represents the input data for an experiment example.

    Attributes:
    - example_id (str): A unique identifier for the example.
    - content (Dict[str, Any]): A dictionary that contains all the necessary input
      parameters for the custom function.
    """

    example_id: str
    content: Dict[str, Any]
