"""
Demo code to translate text from English to Chinese using GPT-3.
"""
import os

from openai import OpenAI

from yival.logger.token_logger import TokenLogger
from yival.schemas.experiment_config import MultimodalOutput
from yival.states.experiment_state import ExperimentState
from yival.wrappers.string_wrapper import StringWrapper


def translate(input: str, state: ExperimentState) -> MultimodalOutput:
    """
    Demo code to translate text from English to Chinese using GPT-3.
    """
    logger = TokenLogger()
    logger.reset()
    # Ensure you have your OpenAI API key set up
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
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
    )

    # Extract the assistant's message (translated text) from the response
    translated_text = MultimodalOutput(
        text_output=response.choices[0].message.content,
    )
    if response.usage is not None:
        token_usage = response.usage.total_tokens
    else:
        token_usage = 0
    logger.log(token_usage)

    return translated_text
