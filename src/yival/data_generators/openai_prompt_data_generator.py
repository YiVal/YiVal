"""
This module provides an implementation for data generation using OpenAI's
model.

The primary goal of this module is to programmatically generate data examples
based on a given prompt and configuration. It employs OpenAI's models to
produce
these examples, and offers utility functions for transforming and processing
the generated data.
"""

import ast
import asyncio
import csv
import os
import pickle
import re
from typing import Any, Dict, Iterator, List

import openai
from tenacity import retry, stop_after_attempt, wait_random_exponential
from tqdm import tqdm

from yival.common import utils
from yival.data_generators.base_data_generator import BaseDataGenerator
from yival.schemas.common_structures import InputData
from yival.schemas.data_generator_configs import OpenAIPromptBasedGeneratorConfig


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


DEFAULT_PROMPT = """
    Please provide a concrete and realistic test case as a dictionary for
    function invocation using the ** operator. Only include parameters,
    excluding description and name. Ensure it's succinct and well-structured.
    **Only provide the dictionary.**
    """


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def completion_with_backpff(**kwargs):
    response = openai.ChatCompletion.create(**kwargs)
    return response


class OpenAIPromptDataGenerator(BaseDataGenerator):
    """
    Data generator using OpenAI's model based on provided prompts and
    configurations.

    This class is responsible for the generation of data examples using
    OpenAI's models.
    The generated data can be used for various purposes, including testing,
    simulations, and more. The nature and number of generated examples are
    determined by the provided configuration.
    """
    config: OpenAIPromptBasedGeneratorConfig
    default_config: OpenAIPromptBasedGeneratorConfig = OpenAIPromptBasedGeneratorConfig(
        prompt=DEFAULT_PROMPT,
        input_function={
            "name": "headline_generation_for_business",
            "description":
            "Given an tech startup business, generate a corresponding landing page headline",
            "parameters": {
                "tech_startup_business": "str"
            }
        },
        number_of_examples=5,
        diversify=False,
    )

    def __init__(self, config: OpenAIPromptBasedGeneratorConfig):
        super().__init__(config)
        self.config = config

    def prepare_messages(self, all_data_content) -> List[Dict[str, Any]]:
        """Prepare the messages for GPT API based on configurations."""
        if not self.config.prompt:
            self.config.prompt = DEFAULT_PROMPT
        if isinstance(self.config.prompt, str):
            content = self.config.prompt + "\n\n Here is the function details \n\n" + dict_to_description(
                self.config.input_function
            )
            if self.config.diversify and all_data_content:
                content += f"\n\n Given the last {min(len(all_data_content), 10)} examples, please generate diverse results to ensure comprehensive evaluation. \nREMEMBER DON'T GENERATE THE SAME SAMPLE AS BELOW! \n\n" + join_dicts_to_string(
                    all_data_content
                )

            return [{"role": "user", "content": content}]

        messages = self.config.prompt
        if self.config.diversify and all_data_content:
            messages.append({
                "role":
                "user",
                "content":
                f"\n\n Given the last {min(len(all_data_content), 10)} examples, please generate diverse results to ensure comprehensive evaluation.\nREMEMBER DON‘T GENERATE THE SAME SAMPLE AS BELOW!  \n\n"
                + join_dicts_to_string(all_data_content)
            })

        return messages

    def process_output(
        self,
        output_content: str,
        all_data: List[InputData],
        chunk: List[InputData],
        fixed_input: Dict[str, Any] | None = {}
    ):
        """Process the output from GPT API and update data lists."""
        generated_example = extract_dict_from_gpt_output(output_content)

        # cut the generated_example keys
        if generated_example:
            keys_to_keep = self.config.input_function.get('parameters',
                                                          {}).keys()
            generated_example = {
                k: generated_example[k]
                for k in keys_to_keep if k in generated_example
            }

        if not generated_example or set(generated_example.keys()) != set(
            self.config.input_function.get('parameters', {}).keys()
        ):
            return

        # choose expected_value
        expected_value = generated_example.get(
            self.config.expected_param_name, None
        )

        if expected_value:
            generated_example.pop(self.config.expected_param_name)
        if fixed_input:
            generated_example.update(fixed_input)
        input_data_instance = InputData(
            example_id=super().generate_example_id(output_content),
            content=generated_example,
            expected_result=expected_value
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

        if not self.config.diversify:
            while len(all_data) < self.config.number_of_examples:
                messages = self.prepare_messages(all_data_content)
                message_batches = [
                    messages
                ] * (self.config.number_of_examples - len(all_data))
                with tqdm(
                    total=self.config.number_of_examples,
                    desc="Generating Examples",
                    unit="example"
                ) as pbar:
                    responses = asyncio.run(
                        utils.parallel_completions(
                            message_batches,
                            self.config.model_name,
                            self.config.max_token,
                            pbar=pbar
                        )
                    )
                for r in responses:
                    self.process_output(
                        r["choices"][0]["message"]["content"],
                        all_data,  # pyright: ignore
                        chunk,
                        self.config.fixed_input  # pyright: ignore
                    )
        else:
            with tqdm(
                total=self.config.number_of_examples,
                desc="Generating Examples",
                unit="example"
            ) as pbar:
                last_len = len(all_data)
                # call_option = self.config.call_option if self.config.call_option else {}
                while len(all_data) < self.config.number_of_examples:
                    messages = self.prepare_messages(all_data_content)
                    output = completion_with_backpff(
                        model=self.config.model_name,
                        messages=messages,
                        n=1,
                        max_tokens=4000,
                        temperature=0.5,
                        request_timeout=20,
                    )
                    self.process_output(  # pyright: ignore
                        output.choices[0].message.content,
                        all_data,
                        chunk,
                        self.config.fixed_input  # pyright: ignore
                    )
                    if len(all_data) > last_len:
                        last_len = len(all_data)
                        pbar.update(1)
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
                print(
                    f"Data succesfully generated and saved to {self.config.output_path}"
                )
        if self.config.output_csv_path:
            with open(self.config.output_csv_path, 'w', newline='') as csvfile:
                rows = [
                    BaseDataGenerator.input_data_to_csv_row(data)
                    for data in all_data
                ]
                header = rows[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=header)
                writer.writeheader()
                for row in rows:
                    writer.writerow(row)
                print(
                    f"Data succesfully generated and saved to {self.config.output_csv_path}"
                )
        if chunk:
            yield chunk


BaseDataGenerator.register_data_generator(
    "openai_prompt_data_generator", OpenAIPromptDataGenerator,
    OpenAIPromptBasedGeneratorConfig
)


def main():
    import time
    start_time = time.time()
    generator = OpenAIPromptDataGenerator(
        OpenAIPromptDataGenerator.default_config
    )
    res = generator.generate_examples()

    for d in res:
        print(d)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Execution time: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    main()
