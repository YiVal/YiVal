import os

from openai import OpenAI

from yival.logger.token_logger import TokenLogger
from yival.schemas.experiment_config import MultimodalOutput
from yival.states.experiment_state import ExperimentState
from yival.wrappers.string_wrapper import StringWrapper


def reply(input: str, state: ExperimentState) -> MultimodalOutput:
    logger = TokenLogger()
    logger.reset()
    # Ensure you have your OpenAI API key set up
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Use the chat-based completion
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role":
            "user",
            "content":
            str(StringWrapper("", name="prompt", state=state)) + f'\n{input}'
        }]
    )

    # Extract the assistant's message (translated text) from the response
    answer = MultimodalOutput(
        text_output=response.choices[0].message.content,
    )
    if response.usage is not None:
        token_usage = response.usage.total_tokens
    else:
        token_usage = 0
    logger.log(token_usage)

    return answer
