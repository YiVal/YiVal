import os

import openai
from openai import OpenAI

from yival.logger.token_logger import TokenLogger
from yival.schemas.experiment_config import MultimodalOutput
from yival.states.experiment_state import ExperimentState
from yival.wrappers.string_wrapper import StringWrapper

# Initialize the OpenAI API key once when the module is imported
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise EnvironmentError(
        "The OPENAI_API_KEY environment variable is not set."
    )


def qa(input: str, state: ExperimentState) -> MultimodalOutput:
    logger = TokenLogger()
    logger.reset()

    # Create a chat message sequence
    qa_string = str(StringWrapper("", name="qa", state=state))
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    try:
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
                "content": f"{input}{qa_string}"
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

    except openai.OpenAIError as e:
        # Handle potential errors from the API call
        raise ValueError(f"An error occurred during the QA process: {e}")
