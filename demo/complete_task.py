import os
import random
import time

import openai
from tenacity import retry, stop_after_attempt, wait_random

from yival.logger.token_logger import TokenLogger
from yival.schemas.experiment_config import MultimodalOutput
from yival.states.experiment_state import ExperimentState
from yival.wrappers.string_wrapper import StringWrapper


@retry(wait=wait_random(min=1, max=20), stop=stop_after_attempt(5))
def completion_with_backpff(**kwargs):
    response = openai.ChatCompletion.create(**kwargs)
    return response


def complete_task(
    task: str,
    **kwargs,
) -> MultimodalOutput:
    state = kwargs.pop("state")
    args = kwargs
    time.sleep(random.choice([1, 2, 3]))
    logger = TokenLogger()
    logger.reset()
    # Ensure you have your OpenAI API key set up
    openai.api_key = os.getenv("OPENAI_API_KEY")

    prompt_lines = ["Complete the following task:", task]
    for key in kwargs.keys():
        prompt_lines.append(f"{key}: {{{key}}}")

    prompt_str = "\n".join(prompt_lines)
    prompt = str(
        StringWrapper(
            prompt_str,
            name="task",
            variables=args,
            state=state,
        )
    )

    model_name = str(
        StringWrapper("gpt-3.5-turbo", name="model_name", state=state)
    )
    prompt_a = [{"content": prompt, "role": "user"}]
    response = completion_with_backpff(
        model="gpt-3.5-turbo",
        messages=prompt_a,
        temperature=0.5,
        n=1,
        max_tokens=1000,
        request_timeout=20
    )
    res = MultimodalOutput(
        text_output=response['choices'][0]['message']['content'],
    )
    token_usage = response['usage']['total_tokens']
    logger.log(token_usage)
    return res


def main():
    res = complete_task(
        task="tiktok script writer",
        ticktok_audience="teens",
        tiktok_cotnent_topic="environment conservation",
        state=ExperimentState()
    )
    print(res)


#"tiktok script writer", ["tiktok_cotnent_topic", "ticktok_audience"]
if __name__ == "__main__":
    main()
