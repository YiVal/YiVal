import os

import openai

from yival.logger.token_logger import TokenLogger
from yival.schemas.experiment_config import MultimodalOutput
from yival.states.experiment_state import ExperimentState
from yival.wrappers.string_wrapper import StringWrapper


def summarize(article: str, state: ExperimentState) -> MultimodalOutput:
    logger = TokenLogger()
    logger.reset()
    # Ensure you have your OpenAI API key set up
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Create a chat message sequence
    messages = [{
        "role":
        "system",
        "content":
        str(
            StringWrapper(
                "You will be given an article, summarize it",
                name="summarization",
                state=state
            )
        )
    }, {
        "role": "user",
        "content": article
    }]
    # Use the chat-based completion
    print(messages)
    response = openai.ChatCompletion.create(model="gpt-4", messages=messages)
    print(response)

    answer = MultimodalOutput(
        text_output=response['choices'][0]['message']['content'],
    )
    token_usage = response['usage']['total_tokens']
    logger.log(token_usage)

    return answer
