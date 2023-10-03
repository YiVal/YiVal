from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Union

from .model_configs import CallOption


@dataclass
class BaseDataGeneratorConfig:
    """
    Base configuration class for all data generators.
    """

    chunk_size: int = 1000
    number_of_examples: int = 10
    output_path: Optional[str] = None

    def asdict(self):
        return asdict(self)


@dataclass
class OpenAIPromptBasedGeneratorConfig(BaseDataGeneratorConfig):
    """
    Generate test cases from prompt. Currently only support openai models.
    """
    model_name: str = "gpt-4"
    prompt: Union[str, List[Dict[str, str]]] = ""
    input_function: Dict[str, Any] = field(default_factory=dict)
    # Whether to diversify the generated examples.
    diversify: bool = True
    max_token = 2000

    # Expected Value name
    expected_param_name: str = ""

    # Llm call option
    call_option: Optional[CallOption] = None

    output_csv_path: Optional[str] = None

    def asdict(self):
        return asdict(self)
