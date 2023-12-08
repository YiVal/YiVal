import os
import random
import time

from openai import OpenAI

from yival.logger.token_logger import TokenLogger
from yival.schemas.experiment_config import MultimodalOutput
from yival.schemas.model_configs import Request
from yival.states.experiment_state import ExperimentState
from yival.wrappers.string_wrapper import StringWrapper


def headline_generation(
    tech_startup_business: str, business: str, target_people: str,
    state: ExperimentState
) -> MultimodalOutput:
    time.sleep(random.choice([1, 2, 3]))
    logger = TokenLogger()
    logger.reset()
    # Ensure you have your OpenAI API key set up
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt = str(
        StringWrapper(
            "Generate landing one page headline for",
            name="task",
            variables={
                "tech_startup_business": tech_startup_business,
                "business": business,
                "target_people": target_people
            },
            state=state,
        )
    )
    model_name = str(
        StringWrapper("gpt-3.5-turbo", name="model_name", state=state)
    )
    response = client.chat.completions.create(
        model=model_name,
        messages=[{
            "role":
            "system",
            "content":
            "You are a helpful assistant that help company grow."
        }, {
            "role":
            "user",
            "content":
            str(
                StringWrapper(
                    "Generate landing one page headline for",
                    name="task",
                    variables={
                        "tech_startup_business": tech_startup_business,
                        "business": business,
                        "target_people": target_people
                    },
                    state=state,
                )
            )
        }],
    )
    res = MultimodalOutput(text_output=response.choices[0].message.content)
    if response.usage is not None:
        token_usage = response.usage.total_tokens
    else:
        token_usage = 0
    logger.log(token_usage)
    return res