"""
Demo code for question answering using GPT-3.
"""
import os

from openai import OpenAI

from yival.logger.token_logger import TokenLogger
from yival.schemas.experiment_config import MultimodalOutput
from yival.states.experiment_state import ExperimentState
from yival.wrappers.string_wrapper import StringWrapper


def qa(question: str, state: ExperimentState) -> MultimodalOutput:
    """
    Demo code for question answering using GPT-3.
    """
    logger = TokenLogger()
    logger.reset()
    # Ensure you have your OpenAI API key set up
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    # Create a chat message sequence
    prompt = str(StringWrapper("", name="qa", state=state))
    # Use the chat-based completion
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role":
            "system",
            "content":
            "You are a helpful assistant that will answer the question with only option."
        }, {
            "role": "user",
            "content": f'{question} ' + prompt
        }],
        temperature=0
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
