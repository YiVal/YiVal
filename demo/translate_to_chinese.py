import os

import openai

from yival.logger.token_logger import TokenLogger
from yival.schemas.experiment_config import MultimodalOutput
from yival.states.experiment_state import ExperimentState
from yival.wrappers.string_wrapper import StringWrapper


def translate_to_chinese(
    input: str, state: ExperimentState
) -> MultimodalOutput:
    logger = TokenLogger()
    logger.reset()
    # Ensure you have your OpenAI API key set up
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Create a chat message sequence
    messages = [{
        "role":
        "system",
        "content":
        "You are a helpful assistant that translates English to any language."
    }, {
        "role":
        "user",
        "content":
        str(
            StringWrapper(
                "Translate the following to Chinese",
                name="translate",
                state=state
            )
        ) + f'{input}'
    }]
    # Use the chat-based completion
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages
    )

    # Extract the assistant's message (translated text) from the response
    translated_text = MultimodalOutput(
        text_output=response['choices'][0]['message']['content'],
    )
    token_usage = response['usage']['total_tokens']
    logger.log(token_usage)

    return translated_text
