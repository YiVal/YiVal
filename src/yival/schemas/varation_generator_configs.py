from dataclasses import asdict, dataclass, field
from typing import List, Optional


@dataclass
class BaseVariationGeneratorConfig:
    """
    Base configuration class for all variation generators.
    """

    number_of_variations: int = 5
    output_path: Optional[str] = None

    def asdict(self):
        return asdict(self)


@dataclass
class OpenAIPromptBasedVariationGeneratorConfig(BaseVariationGeneratorConfig):
    """
    Generate variation using chatgpt. Currently only support openai models.
    """
    openai_model_name: str = "gpt-4"
    input_description: str = "This is a description."
    input_test_cases: List[str] = field(default_factory=list)

    def asdict(self):
        return asdict(self)
