import os
import random
import time

import openai

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

    print(
        f"[INFO] prompt is now {prompt}\n[INFO] tech_startup_business is now {tech_startup_business}\n[INFO] business is now {business}\n[INFO] target_people is now {target_people}"
    )
    messages = [{"role": "user", "content": prompt}]
    # Use the chat-based completion
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages
    )
    res = response['choices'][0]['message']['content']
    token_usage = response['usage']['total_tokens']
    logger.log(token_usage)
    return res
