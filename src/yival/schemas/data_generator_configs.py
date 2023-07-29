from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional


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
    openai_model_name: str = "gpt-4"
    input_function: Dict[str, Any] = field(default_factory=dict)

    def asdict(self):
        return asdict(self)
