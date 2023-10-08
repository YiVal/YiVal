from dataclasses import dataclass

from yival.schemas.varation_generator_configs import BaseVariationGeneratorConfig


@dataclass
class RetrivelVariationGeneratorConfig(BaseVariationGeneratorConfig):
    use_case: str = ""