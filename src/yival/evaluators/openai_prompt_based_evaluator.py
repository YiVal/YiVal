import copy
import os
import string
from typing import Any, Dict, Iterable, List, Optional, Union

import openai

from ..schemas.evaluator_config import (
    EvaluatorOutput,
    EvaluatorType,
    MethodCalculationMethod,
    MetricCalculatorConfig,
    OpenAIPromptBasedEvaluatorConfig,
)
from ..schemas.experiment_config import ExperimentResult, InputData
from .base_evaluator import BaseEvaluator

CLASSIFY_STR = """
First, write out in a step by step manner your reasoning to be sure that your conclusion is correct. Avoid simply stating the correct answer at the outset. Then print only a single choice from {choices} (without quotes or punctuation) on its own line corresponding to the correct answer. At the end, repeat just the answer by itself on a new line.
Reasoning:"""

MATCH_FNS = {
    "include": lambda x, y: float(x in y),
    "exact": lambda x, y: float(x == y),
    "endswith": lambda x, y: x.endswith(y),
    "starts_or_endswith": lambda x, y: x.startswith(y) or x.endswith(y),
}


def get_choice(response: str, choice_strings: Iterable[str]) -> str:
    lines = response.strip().split("\n")
    for line in lines:
        line = line.strip()
        line = "".join(c for c in line if c not in string.punctuation)
        if not line:
            continue
        for choice in choice_strings:
            if MATCH_FNS["starts_or_endswith"](line, choice):
                return choice
    return "invalid response"


def get_choice_score(
    choice: str,
    choice_scores: Optional[Dict[str, float]] = None,
) -> Optional[float]:
    if choice_scores is None:
        return None
    if choice == "invalid response":
        return min(choice_scores.values())
    return choice_scores[choice]


def format_string(
    template: Union[str, List[Dict[str, str]]], content: Dict[str, Any]
) -> Union[str, List[Dict[str, str]]]:

    if isinstance(template, str):
        try:
            return template.format(**content)
        except KeyError as e:
            raise ValueError(f"Missing key {e} in content dictionary")
    res = []
    for t in template:
        formatted_msg = copy.deepcopy(t)
        try:
            if "content" in formatted_msg:
                formatted_msg["content"] = formatted_msg['content'].format(
                    **content
                )
        except KeyError as e:
            raise ValueError(f"Missing key {e} in content dictionary")
        res.append(formatted_msg)

    return res


def choice_to_str(choice_strings: Iterable[str]) -> str:
    """Return a string of choices, e.g. '"Yes" or "No" or "Maybe"'."""
    return " or ".join(f'"{choice}"' for choice in choice_strings)


class OpenAIPromptBasedEvaluator(BaseEvaluator):
    default_config = OpenAIPromptBasedEvaluatorConfig(
        name="openai_prompt_based_evaluator"
    )

    def __init__(self, config: OpenAIPromptBasedEvaluatorConfig):
        super().__init__(config)
        self.config: OpenAIPromptBasedEvaluatorConfig = config

    def evaluate(self, experiment_result: ExperimentResult) -> EvaluatorOutput:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        format_dict = experiment_result.input_data.content
        format_dict["raw_output"] = experiment_result.raw_output
        prompt = format_string(self.config.prompt, format_dict)
        if isinstance(prompt, str):
            prompt = [{"role": "user", "content": prompt}]
        prompt[-1]["content"] += "\n\n" + CLASSIFY_STR.format(
            choices=choice_to_str(self.config.choices)
        )

        response = openai.ChatCompletion.create(model="gpt-4", messages=prompt)
        response = response['choices'][0]['message']['content']
        choice = get_choice(response, self.config.choices)
        score = get_choice_score(choice, self.config.choice_scores)

        return EvaluatorOutput(
            name=self.config.name,
            result=score if score is not None else choice,
            display_name=self.config.display_name,
            metric_calculators=self.config.metric_calculators
        )


BaseEvaluator.register_evaluator(
    "openai_prompt_based_evaluator", OpenAIPromptBasedEvaluator,
    OpenAIPromptBasedEvaluatorConfig
)


def main():
    evaluator_config = OpenAIPromptBasedEvaluatorConfig(
        name="openai_prompt_based_evaluator",
        display_name="math calculator",
        metric_calculators=[
            MetricCalculatorConfig(
                MethodCalculationMethod(MethodCalculationMethod.AVERAGE)
            )
        ],
        prompt="{problem}\n\n Is the answer '{raw_output}' correct? .",
        choices=["Yes", "No"],
        evaluator_type=EvaluatorType.INDIVIDUAL,
        choice_scores={
            "Yes": 1.0,
            "No": 0
        },
    )
    input_data_example = InputData(
        content={
            "problem": "Calculate the area of a circle with radius 5.",
            "method": "Using the formula for the area of a circle: pi*r^2"
        }
    )

    experiment_result_example = ExperimentResult(
        input_data=input_data_example,
        combination={
            "wrapper1": "var1",
            "wrapper2": "var2"
        },
        raw_output="The area of the circle is 78.54 square units.",
        latency=150.0,
        token_usage=50
    )

    generator = OpenAIPromptBasedEvaluator(evaluator_config)
    res = generator.evaluate(experiment_result_example)
    print(res)


if __name__ == "__main__":
    main()
