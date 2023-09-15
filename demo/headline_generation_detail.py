import os
import random
import time

import openai
from yival.common.model_utils import llm_completion
from yival.schemas.model_configs import Request

from yival.logger.token_logger import TokenLogger
from yival.wrappers.string_wrapper import StringWrapper


def headline_generation(
    tech_startup_business: str, business: str, target_people: str
) -> str:
    time.sleep(random.choice([1, 2, 3]))
    logger = TokenLogger()
    logger.reset()
    # Ensure you have your OpenAI API key set up
    openai.api_key = os.getenv("OPENAI_API_KEY")

    prompt = str(
        StringWrapper(
            "Generate landing one page headline for",
            name="task",
            variables={
                "tech_startup_business": tech_startup_business,
                "business": business,
                "target_people": target_people
            }
        )
    )

    response = llm_completion(
        Request(
            model_name=str(
                StringWrapper(
                    "a16z-infra/llama-2-13b-chat:9dff94b1bed5af738655d4a7cbcdcde2bd503aa85c94334fe1f42af7f3dd5ee3",
                    name="model_name"
                )
            ),
            prompt=prompt
        )
    ).output
    res = response['choices'][0]['message']['content']
    token_usage = response['usage']['total_tokens']
    logger.log(token_usage)
    return res
