"""
Demo code to translate text from English to Chinese using GPT-3.
"""
import os

import openai
from litellm import completion

from yival.logger.token_logger import TokenLogger
from yival.wrappers.string_wrapper import StringWrapper


def translate(input: str) -> str:
    """
    Demo code to translate text from English to Chinese using GPT-3.
    """
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
                "Translate the following to Chinese", name="translate"
            )
        ) + f'{input}'
    }]
    response = completion(
        model="gpt-3.5-turbo", messages=messages
    )

    # Extract the assistant's message (translated text) from the response
    translated_text = response['choices'][0]['message']['content']
    token_usage = response['usage']['total_tokens']
    logger.log(token_usage)

    return translated_text
