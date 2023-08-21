import asyncio
import os
import pickle
from typing import Any, Dict, Iterator, List

import openai
from tqdm import tqdm

from ..common import utils
from ..schemas.experiment_config import WrapperVariation
from ..schemas.varation_generator_configs import (
    OpenAIPromptBasedVariationGeneratorConfig,
)
from .base_variation_generator import BaseVariationGenerator

SYSTEM_PRMPOT = """
Your mission is to craft system prompts tailored for GPT-4. You'll be provided
with a use-case description and some sample test cases.
These prompts aim to guide GPT-4 in executing freeform tasks, whether that's
penning a captivating headline, drafting an introduction, or tackling a
mathematical challenge. In your designed prompt, delineate the AI's role using
lucid English. Highlight its perceptual field and the boundaries of its
responses. Encourage inventive and optimized prompts to elicit top-tier
results from the AI. Remember, GPT-4 is self-aware of its AI nature; no need
to reiterate that. The efficacy of your prompt determines your evaluation.
Stay authentic! Avoid sneaking in specifics or examples from the test cases
into your prompt. Such maneuvers will lead to immediate disqualification.
Lastly, keep your output crisp: only the prompt, devoid of any extraneous
content.
"""


def join_array_to_string(list: List[str], last_n=5) -> str:
    to_join = list[-last_n:] if len(list) > last_n else list
    return '\n'.join(map(str, to_join))


def validate_output(output: str, variables: List[str]) -> bool:
    if not variables:
        return True
    """Validate if the generated output contains the required variables in the
    format {var}."""
    return all(f"{{{var}}}" in output for var in variables)


class OpenAIPromptBasedVariationGenerator(BaseVariationGenerator):
    config: OpenAIPromptBasedVariationGeneratorConfig
    default_config = OpenAIPromptBasedVariationGeneratorConfig(
        prompt=[{
            "role": "system",
            "content": SYSTEM_PRMPOT
        }, {
            "role":
            "user",
            "content":
            "Here are some test cases: AI, Weapon\n\n Here is the description of the use-case: Given \{area\}, write a tech startup headline"
        }]
    )

    def __init__(self, config: OpenAIPromptBasedVariationGeneratorConfig):
        super().__init__(config)
        self.config = config

    def prepare_messages(self, res_content) -> List[Dict[str, Any]]:
        last_n = min(len(res_content), 5)
        formatted_variables_str = ', '.join([
            f'{{{var}}}' for var in self.config.variables
        ]) if self.config.variables else ''

        last_examples = f"\n\nGiven the Last {last_n} examples you generated:\n" + join_array_to_string(
            res_content
        ) + "\nplease generate diverse results to ensure comprehensive evaluation" if self.config.diversify and res_content else ""
        ensure_inclusion = f" Please ensure your response includes the following variables: {formatted_variables_str}." if formatted_variables_str else ""

        if isinstance(self.config.prompt, str):
            content = self.config.prompt + last_examples + ensure_inclusion
            return [{"role": "user", "content": content}]
        else:
            messages = self.config.prompt + [{
                "role": "user",
                "content": last_examples
            }, {
                "role": "user",
                "content": ensure_inclusion
            }]
            return [msg for msg in messages if msg["content"]]

    def generate_variations(self) -> Iterator[List[WrapperVariation]]:
        if self.config.output_path and os.path.exists(self.config.output_path):
            with open(self.config.output_path, 'rb') as file:
                yield pickle.load(file)
            return

        res: List[WrapperVariation] = []
        res_content: List[str] = []

        while len(res) < self.config.number_of_variations:
            messages = self.prepare_messages(res_content)
            if not self.config.diversify:
                with tqdm(
                    total=self.config.number_of_variations - len(res),
                    desc="Generating Variations",
                    unit="variation"
                ) as pbar:
                    message_batches = [
                        messages for _ in
                        range(self.config.number_of_variations - len(res))
                    ]
                    responses = asyncio.run(
                        utils.parallel_completions(
                            message_batches,
                            self.config.openai_model_name,
                            self.config.max_tokens,
                            pbar=pbar
                        )
                    )
                    for r in responses:
                        if self.config.variables and not validate_output(
                            r["choices"][0]["message"]["content"],
                            self.config.variables
                        ):
                            continue
                        variation = WrapperVariation(
                            value_type="str",
                            value=r["choices"][0]["message"]["content"]
                        )
                        res.append(variation)
            else:
                with tqdm(
                    total=self.config.number_of_variations,
                    desc="Generating Variations",
                    unit="variation"
                ) as pbar:
                    output = openai.ChatCompletion.create(
                        model=self.config.openai_model_name,
                        messages=messages,
                        temperature=1.3,
                        presence_penalty=2,
                        max_tokens=self.config.max_tokens,
                    )
                    if self.config.variables and not validate_output(
                        output.choices[0].message.content,
                        self.config.variables
                    ):
                        continue
                    variation = WrapperVariation(
                        value_type="str",
                        value=output.choices[0].message.content
                    )
                    res.append(variation)
                    res_content.append(output.choices[0].message.content)
                    pbar.update(1)

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
            prompt=[{
                "role": "system",
                "content": SYSTEM_PRMPOT
            }, {
                "role":
                "user",
                "content":
                "Here are some test cases: AI, Weapon\n\n Here is the description of the use-case: Given \{area\}, write a tech startup headline"
            }],
            number_of_variations=2,
            output_path="test_variation.pkl",
            diversify=False,
            variables=["area"]
        )
    )
    res = generator.generate_variations()
    for d in res:
        print(d)


if __name__ == "__main__":
    main()
