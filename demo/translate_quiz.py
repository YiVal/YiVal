import os

import openai

from yival.common.model_utils import llm_completion
from yival.logger.token_logger import TokenLogger
from yival.schemas.model_configs import Request
from yival.wrappers.string_wrapper import StringWrapper


def translate_quiz(teacher_quiz: str) -> str:
    logger = TokenLogger()
    logger.reset()
    # Ensure you have your OpenAI API key set up
    openai.api_key = os.getenv("OPENAI_API_KEY")
    # messages = [{
    #     "role":
    #     "system",
    #     "content":
    #     "You are a diligent student that translates English to Chinese."
    # }, {
    #     "role":
    #     "user",
    #     "content":
    #     str(
    #         StringWrapper(
    #             "Translate this English text to Chinese: ", name="task"
    #         )
    #     ) + f'{teacher_quiz}'
    # }]
    # response = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo", messages=messages
    # )

    prompt = f"Translate this English text to Chinese: \n Please only output the translated sentence, do not reply with any other content. {teacher_quiz}"
    model_name = str(StringWrapper("", name="model_name"))
    # Use the chat-based completion
    response = llm_completion(
        Request(model_name=model_name, prompt=prompt)
    ).output
    print(f"[DEBUG]response:{response}")
    res = response['choices'][0]['message']['content']
    # token_usage = response['usage']['total_tokens']
    # logger.log(token_usage)
    return res
