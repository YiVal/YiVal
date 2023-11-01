"""
OpenAIPromptBasedEvaluator is an evaluator that uses OpenAI's prompt-based
system for evaluations.

The evaluator interfaces with the OpenAI API to present tasks and interpret
the model's responses to determine the quality or correctness of a given
experiment result.
"""
import copy
import logging
import string
from typing import Any, Dict, Iterable, List, Optional, Union

# for exponential backoff
import openai
from tenacity import before_sleep_log, retry, stop_after_attempt, wait_random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from ..schemas.evaluator_config import (
    EvaluatorOutput,
    EvaluatorType,
    MethodCalculationMethod,
    MetricCalculatorConfig,
    OpenAIPromptBasedEvaluatorConfig,
)
from ..schemas.experiment_config import ExperimentResult, InputData, MultimodalOutput
from .base_evaluator import BaseEvaluator

CLASSIFY_STR = """
First, write out in a step by step manner your reasoning to be sure that your
conclusion is correct.
Avoid simply stating the correct answer at the outset.
Then print only a single choice from {choices} (without quotes or punctuation)
on its own line corresponding to the correct answer.
At the end, repeat just the answer by itself on a new line.
Reasoning:
"""

MATCH_FNS = {
    "include": lambda x, y: float(x in y),
    "exact": lambda x, y: float(x == y),
    "endswith": lambda x, y: x.endswith(y),
    "starts_or_endswith": lambda x, y: x.startswith(y) or x.endswith(y),
}


def extract_choice_from_response(
    response: str, choice_strings: Iterable[str]
) -> str:
    """Extracts the choice from the response string."""
    lines = response.strip().split("\n")
    for line in lines:
        sanitized_line = "".join(
            c for c in line if c not in string.punctuation
        ).strip()
        if not sanitized_line:
            continue
        for choice in choice_strings:
            if MATCH_FNS["exact"](sanitized_line, choice):
                return choice
    return "invalid response"


def calculate_choice_score(
    choice: str,
    choice_scores: Optional[Dict[str, float]] = None
) -> Optional[float]:
    """Calculates the score for the given choice."""
    if choice_scores is None:
        return None
    if choice == "invalid response":
        return min(choice_scores.values())
    return choice_scores.get(choice)


def format_template(
    template: Union[str, List[Dict[str, str]]], content: Dict[str, Any]
) -> Union[str, List[Dict[str, str]]]:
    """Formats a string or list template with the provided content."""
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


@retry(
    wait=wait_random(min=1, max=20),
    stop=stop_after_attempt(100),
    before_sleep=before_sleep_log(logger, logging.DEBUG)
)
def completion_with_backpff(**kwargs):
    response = openai.ChatCompletion.create(**kwargs)
    return response


def choices_to_string(choice_strings: Iterable[str]) -> str:
    """Converts a list of choices into a formatted string."""
    return " or ".join(f'"{choice}"' for choice in choice_strings)


class OpenAIPromptBasedEvaluator(BaseEvaluator):
    """Evaluator using OpenAI's prompt-based evaluation."""

    default_config = OpenAIPromptBasedEvaluatorConfig(
        name="openai_prompt_based_evaluator"
    )

    def __init__(self, config: OpenAIPromptBasedEvaluatorConfig):
        super().__init__(config)
        self.config = config

    def evaluate(self, experiment_result: ExperimentResult) -> EvaluatorOutput:
        """Evaluate the experiment result using OpenAI's prompt-based evaluation."""
        assert isinstance(self.config, OpenAIPromptBasedEvaluatorConfig)
        format_dict = copy.deepcopy(experiment_result.input_data.content)
        format_dict["raw_output"] = experiment_result.raw_output.text_output

        prompt = format_template(self.config.prompt, format_dict)
        if isinstance(prompt, str):
            prompt = [{"role": "user", "content": prompt}]

        prompt[-1]["content"] += "\n\n" + CLASSIFY_STR.format(
            choices=choices_to_string(self.config.choices)
        )
        response = completion_with_backpff(
            model="gpt-4",
            messages=prompt,
            temperature=0.5,
            n=1,
            max_tokens=1000,
            request_timeout=60,
        )
        #response = openai.ChatCompletion.create(model="gpt-4", messages=prompt, temperature=0.5)
        response_content = response['choices'][0]['message']['content']
        choice = extract_choice_from_response(
            response_content, self.config.choices
        )
        score = calculate_choice_score(choice, self.config.choice_scores)
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
    """Main function to test the OpenAIPromptBasedEvaluator."""
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
        raw_output=MultimodalOutput(
            text_output="The area of the circle is 78.54 square units."
        ),
        latency=150.0,
        token_usage=50
    )

    evaluator = OpenAIPromptBasedEvaluator(evaluator_config)
    result = evaluator.evaluate(experiment_result_example)
    print(result)


if __name__ == "__main__":
    main()
