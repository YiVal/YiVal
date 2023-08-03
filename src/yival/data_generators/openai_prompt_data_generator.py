import ast
import os
import pickle
import re
from typing import Any, Dict, Iterator, List

import openai

from ..schemas.common_structures import InputData
from ..schemas.data_generator_configs import OpenAIPromptBasedGeneratorConfig
from .base_data_generator import BaseDataGenerator


def dict_to_description(data, indent=0):
    narrative = []
    for key, value in data.items():
        prefix = '  ' * indent
        if key == "parameters":
            param_str = ', '.join(
                f"'{k}' of type '{v}'" for k, v in value.items()
            )
            narrative.append(f"{prefix}- It takes parameters: {param_str}.")
        elif isinstance(value, dict):
            sub_narrative = dict_to_description(value, indent + 1)
            narrative.append(
                f"{prefix}- '{key}' has the following properties:\n{sub_narrative}"
            )
        elif isinstance(value, list):
            items = ', '.join(map(str, value))
            narrative.append(f"{prefix}- '{key}' can have values: {items}.")
        else:
            narrative.append(f"{prefix}- '{key}' is described as '{value}'.")
    return '\n'.join(narrative)


def extract_dict_from_gpt_output(output) -> Dict[str, Any] | None:
    pattern = r"\{[^}]+\}"
    match = re.search(pattern, output)
    dict_string = match.group(0) if match else None
    if dict_string:
        try:
            return ast.literal_eval(dict_string.replace("'", "\""))
        except Exception:
            return None
    return None


def join_dicts_to_string(dicts: List[Dict[Any, Any]], last_n=10) -> str:
    to_join = dicts[-last_n:] if len(dicts) > last_n else dicts
    return '\n'.join(map(str, to_join))


class OpenAIPromptDataGenerator(BaseDataGenerator):
    config: OpenAIPromptBasedGeneratorConfig
    default_config: OpenAIPromptBasedGeneratorConfig = OpenAIPromptBasedGeneratorConfig(
        prompt=
        """ Please provide a single test case in the form of a dictionary suitable for passing to the function using the ** operator.
    Parameter only and don't include description and name. 
    Ideally the test cases should be concrete and realistic. Be attractive.
    ### Dictionary only and nothing else ####""",
        input_function={
            "name": "headline_generation_for_business",
            "description":
            "Given an tech startup business, generate a corresponding landing page headline",
            "parameters": {
                "tech_startup_business": "str"
            }
        },
        number_of_examples=20,
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
        while len(all_data) < self.config.number_of_examples:
            if isinstance(self.config.prompt, str):
                content = self.config.prompt + "\n\n Here is the function details \n\n" + dict_to_description(
                    self.config.input_function
                )
                if self.config.diversify:
                    content += "\n\n Here are last 10 examples, try to diversify the results for robust evaluation. \n\n" + join_dicts_to_string(
                        all_data
                    )
                messages = [{"role": "user", "content": content}]
            else:
                messages = self.config.prompt
                if self.config.diversify:
                    messages.append({
                        "role":
                        "user",
                        "content":
                        "\n\n Here are last 10 examples, try to diversify the results robust evaluation. \n\n"
                        + join_dicts_to_string(all_data)
                    })

            output = openai.ChatCompletion.create(
                model=self.config.openai_model_name,
                messages=messages,
                temperature=1.3,
                presence_penalty=2,
            )
            generated_example = extract_dict_from_gpt_output(
                output.choices[0].message.content
            )

            if not generated_example or generated_example.keys(
            ) != self.config.input_function.get('parameters', {}).keys():
                continue

            input_data_instance = InputData(
                example_id=super().generate_example_id(
                    output.choices[0].message.content
                ),
                content=generated_example,
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
        OpenAIPromptDataGenerator.default_config
    )
    res = generator.generate_examples()
    for d in res:
        print(d)


if __name__ == "__main__":
    main()
