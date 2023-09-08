from dataclasses import asdict, dataclass
from typing import Dict, List, Optional, Union


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
    model_name: str = "gpt-4"
    prompt: Union[str, List[Dict[str, str]]] = ""
    diversify: bool = False
    variables: Optional[List[str]] = None
    max_tokens: int = 7000

    def asdict(self):
        return asdict(self)
