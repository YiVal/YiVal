"""
Demo code for question answering using GPT-3.
"""
import os

import openai
from litellm import completion

from yival.logger.token_logger import TokenLogger
from yival.wrappers.string_wrapper import StringWrapper


def qa(question: str) -> str:
    """
    Demo code for question answering using GPT-3.
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
        "You are a helpful assistant that will answer the question with only option."
    }, {
        "role": "user",
        "content": f'{question} ' + str(StringWrapper("", name="qa"))
    }]
    # Use the chat-based completion
    response = completion(
        model="gpt-3.5-turbo", messages=messages, temperature=0
    )

    # Extract the assistant's message (translated text) from the response
    answer = response['choices'][0]['message']['content']
    token_usage = response['usage']['total_tokens']
    logger.log(token_usage)

    return answer
