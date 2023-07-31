import os
import pickle
from typing import Iterator, List

import openai

from ..schemas.experiment_config import WrapperVariation
from ..schemas.varation_generator_configs import (
    OpenAIPromptBasedVariationGeneratorConfig,
)
from .base_variation_generator import BaseVariationGenerator

SYSTEM_PRMPOT = """
Your mission is to craft system prompts tailored for GPT-4. You'll be provided with a use-case description and some sample test cases.
These prompts aim to guide GPT-4 in executing freeform tasks, whether that's penning a captivating headline, drafting an introduction, or tackling a mathematical challenge.
In your designed prompt, delineate the AI's role using lucid English. Highlight its perceptual field and the boundaries of its responses. Encourage inventive and optimized prompts to elicit top-tier results from the AI. Remember, GPT-4 is self-aware of its AI nature; no need to reiterate that.
The efficacy of your prompt determines your evaluation. Stay authentic! Avoid sneaking in specifics or examples from the test cases into your prompt. Such maneuvers will lead to immediate disqualification.
Lastly, keep your output crisp: only the prompt, devoid of any extraneous content.
"""


class OpenAIPromptBasedVariationGenerator(BaseVariationGenerator):
    config: OpenAIPromptBasedVariationGeneratorConfig
    default_config: OpenAIPromptBasedVariationGeneratorConfig = OpenAIPromptBasedVariationGeneratorConfig(
    )

    def __init__(self, config: OpenAIPromptBasedVariationGeneratorConfig):
        super().__init__(config)
        self.config = config

    def generate_variations(self) -> Iterator[List[WrapperVariation]]:

        if self.config.output_path and os.path.exists(self.config.output_path):
            with open(self.config.output_path, 'rb') as file:
                all_data = pickle.load(file)
                yield all_data
            return
        res = []
        test_cases_string = '\n'.join(self.config.input_test_cases)
        test_cases = f"Here are some test cases:\n{test_cases_string}" if self.config.input_test_cases else ""
        for i in range(self.config.number_of_variations):
            output = openai.ChatCompletion.create(
                model=self.config.openai_model_name,
                messages=[{
                    "role": "system",
                    "content": SYSTEM_PRMPOT
                }, {
                    "role":
                    "user",
                    "content":
                    f"{test_cases}" +
                    f"Here is the description of the task {self.config.input_description}\n\nRespond with your prompt, and nothing else. Be creative."
                }],
                temperature=0.9,
            )
            variation = WrapperVariation(
                value_type="str",
                value=output.choices[0].message.content,
            )

            res.append(variation)

        if self.config.output_path:
            with open(self.config.output_path, 'wb') as file:
                pickle.dump(res, file)

        if res:
            yield res


BaseVariationGenerator.register_variation_generator(
    "openai_prompt_based_variation_generator",
    OpenAIPromptBasedVariationGenerator,
    OpenAIPromptBasedVariationGeneratorConfig
)


def main():
    generator = OpenAIPromptBasedVariationGenerator(
        OpenAIPromptBasedVariationGeneratorConfig(
            input_test_cases=["AI law firm", "AI sales agent"],
            number_of_variations=3,
            input_description=
            "Given an tech startup business, generate corresponding landing page headlines",
            output_path="variation.pkl"
        )
    )
    res = generator.generate_variations()
    for d in res:
        print(d)


if __name__ == "__main__":
    main()
