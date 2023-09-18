import os

import openai

from yival.logger.token_logger import TokenLogger
from yival.states.experiment_state import ExperimentState
from yival.wrappers.string_wrapper import StringWrapper


def qa(input: str, state: ExperimentState) -> str:
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
        "role":
        "user",
        "content":
        f'{input}' + str(StringWrapper("", name="qa", state=state))
    }]
    # Use the chat-based completion
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages
    )

    # Extract the assistant's message (translated text) from the response
    answer = response['choices'][0]['message']['content']
    token_usage = response['usage']['total_tokens']
    logger.log(token_usage)

    return answer
