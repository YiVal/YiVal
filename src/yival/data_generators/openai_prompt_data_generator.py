import ast
import asyncio
import os
import pickle
import re
from typing import Any, Dict, Iterator, List

import openai

from ..common import utils
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
        prompt="""
            Please provide a concrete and realistic test case as a dictionary for function invocation using the ** operator.
            Only include parameters, excluding description and name.
            Ensure it's succinct and well-structured.
            **Only provide the dictionary.**
            """,
        input_function={
            "name": "headline_generation_for_business",
            "description":
            "Given an tech startup business, generate a corresponding landing page headline",
            "parameters": {
                "tech_startup_business": "str"
            }
        },
        number_of_examples=5,
        diversify=True,
    )

    def __init__(self, config: OpenAIPromptBasedGeneratorConfig):
        super().__init__(config)
        self.config = config

    def prepare_messages(self, all_data_content) -> List[Dict[str, Any]]:
        """Prepare the messages for GPT API based on configurations."""
        if isinstance(self.config.prompt, str):
            content = self.config.prompt + "\n\n Here is the function details \n\n" + dict_to_description(
                self.config.input_function
            )
            if self.config.diversify and all_data_content:
                content += f"\n\n Given the last {min(len(all_data_content), 10)} examples, please generate diverse results to ensure comprehensive evaluation. \n\n" + join_dicts_to_string(
                    all_data_content
                )
            return [{"role": "user", "content": content}]
        else:
            messages = self.config.prompt
            if self.config.diversify and all_data_content:
                messages.append({
                    "role":
                    "user",
                    "content":
                    f"\n\n Given the last {min(len(all_data_content), 10)} examples, please generate diverse results to ensure comprehensive evaluation. \n\n"
                    + join_dicts_to_string(all_data_content)
                })

            return messages

    def process_output(
        self, output_content: str, all_data: List[InputData],
        chunk: List[InputData]
    ):
        """Process the output from GPT API and update data lists."""
        generated_example = extract_dict_from_gpt_output(output_content)
        if not generated_example or set(generated_example.keys()) != set(
            self.config.input_function.get('parameters', {}).keys()
        ):
            return
        input_data_instance = InputData(
            example_id=super().generate_example_id(output_content),
            content=generated_example,
            expected_result=None
        )
        all_data.append(input_data_instance)
        chunk.append(input_data_instance)

    def generate_examples(self) -> Iterator[List[InputData]]:
        all_data: List[InputData] = []
        # Loading data from existing path if exists
        if self.config.output_path and os.path.exists(self.config.output_path):
            with open(self.config.output_path, 'rb') as file:
                all_data = pickle.load(file)
                for i in range(0, len(all_data), self.config.chunk_size):
                    yield all_data[i:i + self.config.chunk_size]
            return
        chunk: List[InputData] = []
        all_data_content: List[Dict[str, Any]] = []

        while (len(all_data) < self.config.number_of_examples):
            messages = self.prepare_messages(all_data_content)
            if not self.config.diversify:
                message_batches = [
                    messages
                ] * (self.config.number_of_examples - len(all_data))
                responses = asyncio.run(
                    utils.parallel_completions(
                        message_batches, self.config.openai_model_name, 1000
                    )
                )
                for r in responses:
                    self.process_output(
                        r["choices"][0]["message"]["content"], all_data, chunk
                    )
            else:
                output = openai.ChatCompletion.create(
                    model=self.config.openai_model_name,
                    messages=messages,
                    temperature=1.3,
                    presence_penalty=2,
                )
                self.process_output(
                    output.choices[0].message.content, all_data, chunk
                )
                c = extract_dict_from_gpt_output(
                    output.choices[0].message.content
                )
                if c:
                    all_data_content.append(c)
            if chunk and len(chunk) >= self.config.chunk_size:
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
