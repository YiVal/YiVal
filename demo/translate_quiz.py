import os

import openai
from openai import OpenAI

from yival.logger.token_logger import TokenLogger
from yival.schemas.experiment_config import MultimodalOutput
from yival.schemas.model_configs import Request
from yival.states.experiment_state import ExperimentState
from yival.wrappers.string_wrapper import StringWrapper

# Initialize the OpenAI API key once when the module is imported
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise EnvironmentError(
        "The OPENAI_API_KEY environment variable is not set."
    )


def translate_quiz(
    teacher_quiz: str, state: ExperimentState
) -> MultimodalOutput:
    logger = TokenLogger()
    logger.reset()

    translation_prompt = f"Instruction: Translate this English text to Chinese: \n {teacher_quiz}"
    model_name = str(StringWrapper("", name="model_name", state=state))

    try:
        # Use the chat-based completion
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model=model_name,
            messages=[{
                "role": "user",
                "content": translation_prompt
            }],
        )
        translated_text = response.choices[0].message.content
        if response.usage is not None:
            token_usage = response.usage.total_tokens
        else:
            token_usage = 0
        logger.log(token_usage)

        return MultimodalOutput(text_output=translated_text)

    except openai.APIError as e:
        # Handle any error that occurs during the API call
        raise ValueError(f"An error occurred while translating: {e}")
