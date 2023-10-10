from typing import Iterator, List

from ..schemas.experiment_config import WrapperVariation
from ..schemas.varation_generator_configs import BaseVariationGeneratorConfig
from .base_variation_generator import BaseVariationGenerator

PROMPT = """

I will provide you with piece of content (e.g. articles, papers, documentation,
etc.)

        You will generate increasingly concise, entity-dense summaries of the
        content.

        Repeat the following 2 steps 5 times.

        Step 1. Identify 1-3 informative Entities (";" delimited) from the
        Article which are missing from the previously generated summary.

        Step 2. Write a new, denser summary of identical length which covers 
        every entity and detail from the previous summary plus the Missing 
        Entities.

        A Missing Entity is:

        Relevant: to the main story.
        Specific: descriptive yet concise (5 words or fewer).
        Novel: not in the previous summary.
        Faithful: present in the content piece.
        Anywhere: located anywhere in the Article.

        Guidelines:

        The first summary should be long (4-5 sentences, ~80 words) yet highly 
        non-specific, containing little information beyond the entities marked 
        as missing. Use overly verbose language and fillers
        (e.g., "this article discusses") to reach -80 words.
        Make every word count: re-write the previous summary to improve flow 
        and make space for additional entities.
        Make space with fusion, compression, and removal of uninformative
        phrases like "the article discusses".
        The summaries should become highly dense and concise yet 
        self-contained, e.g., easily understood without the Article.
        Missing entities can appear anywhere in the new summary.
        Never drop entities from the previous summary. If space cannot be made, 
        add fewer new entities.
        Remember, use the exact same number of words for each summary.
        Answer in JSON. The JSON should be a list (length 5) of dictionaries 
        whose keys are "Missing_Entities" and "Denser_Summary".


"""


class ChainOfDensityPromptGenerator(BaseVariationGenerator):
    config: BaseVariationGeneratorConfig
    default_config = BaseVariationGeneratorConfig()

    def __init__(self, config: BaseVariationGeneratorConfig):
        super().__init__(config)
        self.config = config

    def generate_variations(self) -> Iterator[List[WrapperVariation]]:
        res: List[WrapperVariation] = [
            WrapperVariation(value_type="str", value=PROMPT)
        ]
        yield res


BaseVariationGenerator.register_variation_generator(
    "chain_of_density_prompt_generator",
    ChainOfDensityPromptGenerator,
    BaseVariationGeneratorConfig,
)
