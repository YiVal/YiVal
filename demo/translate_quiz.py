import os

import openai

from yival.common.model_utils import llm_completion
from yival.logger.token_logger import TokenLogger
from yival.schemas.experiment_config import MultimodalOutput
from yival.schemas.model_configs import Request
from yival.wrappers.string_wrapper import StringWrapper


def translate_quiz(teacher_quiz: str) -> MultimodalOutput:
    logger = TokenLogger()
    logger.reset()
    # Ensure you have your OpenAI API key set up
    openai.api_key = os.getenv("OPENAI_API_KEY")

    prompt = f"Instruction: Translate this English text to Chinese: \n {teacher_quiz}"
    model_name = str(StringWrapper("", name="model_name"))
    # Use the chat-based completion
    response = llm_completion(
        Request(model_name=model_name, prompt=prompt)
    ).output
    res = MultimodalOutput(
        text_output=response['choices'][0]['message']['content'],
    )
    token_usage = response['usage']['total_tokens']
    logger.log(token_usage)
    return res
