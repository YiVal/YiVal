# common_structures.py
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class InputData:
    """
    Represents the input data for an experiment example.

    Attributes:
    - example_id Optional[str]: A unique identifier for the example.
    - content (Dict[str, Any]): A dictionary that contains all the necessary input
      parameters for the custom function.
    - expected_result (Optional[Any]): The expected result given the input.
    """

    content: Dict[str, Any]
    example_id: Optional[str] = None
    expected_result: Optional[Any] = None

    def asdict(self) -> Dict[str, Any]:
        return {
            "example_id": self.example_id,
            "content": self.content,
            "expected_result": self.expected_result
        }

    def __repr__(self):
        content_str = ", ".join([
            f'"{k}": "{v}"' for k, v in self.content.items()
        ])
        expected_result_str = f'"{self.expected_result}"' if self.expected_result is not None else "None"
        return f'{{"example_id" : "{self.example_id}", "content" : {{{content_str}}}, "expected_result" : {expected_result_str}}}'
