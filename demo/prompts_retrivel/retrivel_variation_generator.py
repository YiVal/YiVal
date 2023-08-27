import csv
from typing import Iterator, List

import faiss  # pylint: disable=import-error
import openai
from langchain.docstore import InMemoryDocstore
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.vectorstores import FAISS
from yival.evaluators.openai_prompt_based_evaluator import (
    CLASSIFY_STR,
    choices_to_string,
    extract_choice_from_response,
)
from yival.schemas.experiment_config import WrapperVariation
from yival.variation_generators.base_variation_generator import (
    BaseVariationGenerator,
)

from .retrivel_variation_generator_config import (
    RetrivelVariationGeneratorConfig,
)

PROMPT_GENERATION_PROMPT = """
Your mission is to craft system prompts tailored for GPT-4. You'll be provided
with a use-case description.
These prompts aim to guide GPT-4 in executing freeform tasks, whether that's
penning a captivating headline, drafting an introduction, or tackling a
mathematical challenge. In your designed prompt, delineate the AI's role using
lucid English. Highlight its perceptual field and the boundaries of its
responses. Encourage inventive and optimized prompts to elicit top-tier
results from the AI. Remember, GPT-4 is self-aware of its AI nature; no need
to reiterate that. The efficacy of your prompt determines your evaluation.
Stay authentic! Avoid sneaking in specifics into your prompt.
Such maneuvers will lead to immediate disqualification.
Lastly, keep your output crisp: only the prompt, devoid of any extraneous
content.
"""


def process_csv(filename):
    prompts = []

    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            prompt = row['prompt']
            # Split at "my first" and take the part before it.
            processed_prompt = prompt.lower().split('my first', 1)[0]
            prompts.append(processed_prompt)

    return prompts


def assign_labels_formatted(options):
    # Ensure the input list has at most 3 items
    if len(options) > 3:
        raise ValueError("The input list must have at most 3 items.")

    # List to store the formatted strings
    formatted_list = []
    choices = []
    # Assign labels and append to the formatted list
    if len(options) == 1:
        formatted_list.append(f"A {options[0]}")
        formatted_list.append("B None of the above")
        choices = ["A", "B"]
    elif len(options) == 2:
        formatted_list.append(f"A {options[0]}")
        formatted_list.append(f"B {options[1]}")
        formatted_list.append("C None of the above")
        choices = ["A", "B", "C"]
    elif len(options) == 3:
        formatted_list.append(f"A {options[0]}")
        formatted_list.append(f"B {options[1]}")
        formatted_list.append(f"C {options[2]}")
        formatted_list.append("D None of the above")
        choices = ["A", "B", "C", "D"]
    result = '\n'.join(formatted_list)
    return result, choices


class RetrivelVariationGenerator(BaseVariationGenerator):

    def __init__(self, config: RetrivelVariationGeneratorConfig):
        super().__init__(config)
        self.config = config
        documents = []
        prompts = process_csv('demo/data/prompts.csv')
        for prompt in prompts:
            documents.append(Document(page_content=prompt, metadata={}))
        self.retriever = FAISS(
            OpenAIEmbeddings(client=None).embed_query,
            faiss.IndexFlatL2(1536),  # Dimensions of the OpenAIEmbeddings
            InMemoryDocstore({}),
            {},
        ).as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "score_threshold": 0.5,
                "k": 3
            },
        )
        self.retriever.add_documents(documents)

    def generate_variations(self) -> Iterator[List[WrapperVariation]]:
        documents = self.retriever.get_relevant_documents(
            self.config.use_case
        )  # type: ignore
        options = [doc.page_content for doc in documents]
        choices, choices_strings = assign_labels_formatted(options)
        prompt_generation_message = [{
            "role": "system",
            "content": PROMPT_GENERATION_PROMPT
        }]
        prompt_generation_message.append({
            "role":
            "user",
            "content":
            f"use case: {self.config.use_case}"  # type: ignore
        })
        if len(documents) == 0:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=prompt_generation_message,
                temperature=0.0
            )
            variation = WrapperVariation(
                value_type="str",
                value=response['choices'][0]['message']['content']
            )
            yield [variation]

        prompt = "You are assessing prompts candidate based on the use case\n"
        prompt += f"{self.config.use_case}\n"  # type: ignore
        prompt += "You have the following options:\n"
        prompt += choices
        prompt += "\n\n" + CLASSIFY_STR.format(
            choices=choices_to_string(choices_strings)
        )
        messages = [{"role": "user", "content": prompt}]
        response = openai.ChatCompletion.create(
            model="gpt-4", messages=messages, temperature=0.0
        )
        response_content = response['choices'][0]['message']['content']
        choice = extract_choice_from_response(
            response_content, choices_strings
        )

        if choice == choices_strings[-1]:
            response = openai.ChatCompletion.create(
                model="gpt-4-32k",
                messages=prompt_generation_message,
                temperature=0.5
            )
            variation = WrapperVariation(
                value_type="str",
                value=response['choices'][0]['message']['content']
            )
            yield [variation]
        else:
            if choice == "A":
                variation = WrapperVariation(
                    value_type="str", value=options[0]
                )
                yield [variation]
            elif choice == "B":
                variation = WrapperVariation(
                    value_type="str", value=options[1]
                )
                yield [variation]
            elif choice == "C":
                variation = WrapperVariation(
                    value_type="str", value=options[2]
                )
                yield [variation]


def main():
    generator = RetrivelVariationGenerator(
        RetrivelVariationGeneratorConfig(use_case="write shell scripts")
    )
    while True:  # Start the infinite loop
        use_case_input = input(
            "Please enter a use case (or type 'exit' to quit): "
        )
        if use_case_input.strip().lower() == 'exit':
            break
        generator.config.use_case = use_case_input
        for r in generator.generate_variations():
            print(r)


if __name__ == '__main__':
    main()
