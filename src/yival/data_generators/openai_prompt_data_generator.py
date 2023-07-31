import ast
import os
import pickle
import re
from typing import Iterator, List

import openai

from ..schemas.common_structures import InputData
from ..schemas.data_generator_configs import OpenAIPromptBasedGeneratorConfig
from .base_data_generator import BaseDataGenerator


def dict_to_description(data, indent=0):
    """Recursively converts a dictionary into a descriptive narrative, handling function parameters."""

    narrative = []

    for key, value in data.items():
        if key == "parameters":
            # Handle the special 'parameters' key
            param_descriptions = [
                f"'{param_name}' of type '{param_type}'"
                for param_name, param_type in value.items()
            ]
            param_str = ', '.join(param_descriptions)
            narrative.append(
                f"{'  ' * indent}- It takes parameters: {param_str}."
            )
        elif isinstance(value, dict):
            narrative.append(
                f"{'  ' * indent}- '{key}' has the following properties:\n{dict_to_description(value, indent + 1)}"
            )
        elif isinstance(value, list):
            items = ', '.join([str(item) for item in value])
            narrative.append(
                f"{'  ' * indent}- '{key}' can have values: {items}."
            )
        else:
            narrative.append(
                f"{'  ' * indent}- '{key}' is described as '{value}'."
            )

    return '\n'.join(narrative)


def extract_dict_from_gpt_output(output):
    # Regular expression to capture content within curly braces
    pattern = r"\{[^}]+\}"

    # Search for the dictionary pattern in the GPT output
    match = re.search(pattern, output)
    dict_string = match.group(0) if match else None
    if dict_string:
        # Convert single quotes to double quotes for JSON parsing and then evaluate
        return ast.literal_eval(dict_string.replace("'", "\""))
    return None


class OpenAIPromptDataGenerator(BaseDataGenerator):
    config: OpenAIPromptBasedGeneratorConfig
    default_config: OpenAIPromptBasedGeneratorConfig = OpenAIPromptBasedGeneratorConfig(
        input_function={
            "name": "headline_generation_for_business",
            "description":
            "Given an tech startup business, generate corresponding landing page headlines",
            "parameters": {
                "tech_startup_business": "str"
            }
        }
    )

    def __init__(self, config: OpenAIPromptBasedGeneratorConfig):
        super().__init__(config)
        self.config = config

    def generate_examples(self) -> Iterator[List[InputData]]:

        if self.config.output_path and os.path.exists(self.config.output_path):
            with open(self.config.output_path, 'rb') as file:
                all_data = pickle.load(file)
                for i in range(0, len(all_data), self.config.chunk_size):
                    yield all_data[i:i + self.config.chunk_size]
            return

        chunk = []
        all_data = []
        for i in range(self.config.number_of_examples):
            output = openai.ChatCompletion.create(
                model=self.config.openai_model_name,
                messages=[{
                    "role":
                    "system",
                    "content":
                    "You are a helpful assistant. Parse the following user input and provide a dictionary from the description."
                }, {
                    "role":
                    "user",
                    "content":
                    f"""
    Based on the function details:
    {dict_to_description(self.config.input_function)}

    Please provide a single test case in the form of a dictionary suitable for passing to the function using the ** operator.
    Ideally the test cases should be concrete and realistic.
    ### Dictionary only and nothing else ####
    """
                }],
                temperature=0.9,
            )
            input_data_instance = InputData(
                example_id=super().generate_example_id(
                    output.choices[0].message.content
                ),
                content=extract_dict_from_gpt_output(
                    output.choices[0].message.content
                ),
                expected_result=None
            )
            all_data.append(input_data_instance)
            chunk.append(input_data_instance)
            if len(chunk) >= self.config.chunk_size:
                yield chunk
                chunk = []

        if self.config.output_path:
            with open(self.config.output_path, 'wb') as file:
                pickle.dump(all_data, file)
        if chunk:
            yield chunk


BaseDataGenerator.register_data_generator(
    "openai_prompt_data_generator", OpenAIPromptDataGenerator,
    OpenAIPromptBasedGeneratorConfig
)


def main():
    generator = OpenAIPromptDataGenerator(
        OpenAIPromptBasedGeneratorConfig(
            input_function={
                "name": "headline_generation_for_business",
                "description":
                "Given an tech startup business, generate corresponding landing page headlines",
                "parameters": {
                    "tech_startup_business": "str"
                }
            },
            number_of_examples=3,
            output_path="test.pkl"
        )
    )
    res = generator.generate_examples()
    for d in res:
        print(d)


if __name__ == "__main__":
    main()
