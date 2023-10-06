from typing import Iterator, List

from yival.schemas.experiment_config import WrapperVariation
from yival.schemas.varation_generator_configs import (
    SelfExemplarConfig,
)
from yival.variation_generators.base_variation_generator import BaseVariationGenerator


def construct_prompt(config: SelfExemplarConfig) -> str:
    core_concept_section = f"""
## Core Concept:
{config.core_concept_prompt}
""" if config.core_concept_prompt else ""

    tutorial_section = f"""
## Tutorial:
{config.tutorial_prompt}
""" if config.tutorial_prompt else ""

    prompt = f"""
{config.start_prompt}
# Problem:
{config.problem_prompt}

# Instructions:
## Relevant Problems:
{config.relevant_problems_prompt}
{core_concept_section}
{tutorial_section}
## Solve the Initial Problem:
{config.end_prompt}
"""
    return prompt.strip()


class SelfExemplar(BaseVariationGenerator):
    config: SelfExemplarConfig
    default_config: SelfExemplarConfig

    def __init__(self, config: SelfExemplarConfig):
        super().__init__(config)
        self.config = config

    def generate_variations(self) -> Iterator[List[WrapperVariation]]:
        res: List[WrapperVariation] = [
            WrapperVariation(
                value_type="str", value=construct_prompt(self.config)
            )
        ]
        yield res


BaseVariationGenerator.register_variation_generator(
    "self_exemplar",
    SelfExemplar,
    SelfExemplarConfig,
)


def main():
    generator = SelfExemplar(
        SelfExemplarConfig(
            start_prompt=(
                "Your task is to tackle mathematical problems. When presented with a "
                "math problem, recall relevant problems as examples. Afterward, proceed "
                "to solve the initial problem."
            ),
            problem_prompt=(
                "An airline serves a dinner to all the passengers on an airplane. They get "
                "their choice of steak or fish. Three steak meals and three fish meals are "
                "set aside for the six-member crew. If the meals are distributed to the crew "
                "members randomly, what is the probability that both pilots get the fish?"
            ),
            relevant_problems_prompt=(
                "Recall three examples of math problems that are relevant to the initial "
                "problem. Your problems should be distinct from each other and from the initial "
                "problem (e.g., involving different numbers and names). For each problem: \n"
                " - After \"Q: \", describe the problem \n"
                " - After \"A: \", explain the solution and enclose the ultimate answer in \\boxed{}."
            ),
            core_concept_prompt=(
                "Identify the core concepts or algorithms used to solve the problem."
            ),
            tutorial_prompt=("Write a tutorial about these concepts."),
            end_prompt=(
                "Q: Copy and paste the initial problem here. \n"
                "A: Explain the solution and enclose the ultimate answer in \\boxed{} here."
            )
        )
    )

    res = generator.generate_variations()
    for d in res:
        print(d[0].value)


if __name__ == "__main__":
    main()
