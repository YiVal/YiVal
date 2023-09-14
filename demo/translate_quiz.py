import os

import openai

from yival.logger.token_logger import TokenLogger
from yival.wrappers.string_wrapper import StringWrapper


def translate_quiz(teacher_quiz: str) -> str:
    logger = TokenLogger()
    logger.reset()
    # Ensure you have your OpenAI API key set up
    openai.api_key = os.getenv("OPENAI_API_KEY")
    messages = [{
        "role":
        "system",
        "content":
        "You are a diligent student that translates English to Chinese."
    }, {
        "role":
        "user",
        "content":
        str(
            StringWrapper(
                "Translate this English text to Chinese: ", name="task"
            )
        ) + f'{teacher_quiz}'
    }]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages
    )
    # prompt = str(
    #     StringWrapper(
    #         "Translate this English text to Chinese:",
    #         name="task",
    #         variables={
    #             "teacher_quiz": teacher_quiz,
    #         }
    #     )
    # )
    # # Use the chat-based completion
    # response = llm_completion(
    #     Request(
    #         model_name=str(StringWrapper("a16z-infra/llama-2-13b-chat:9dff94b1bed5af738655d4a7cbcdcde2bd503aa85c94334fe1f42af7f3dd5ee3", name="model_name")),
    #         prompt=prompt
    #     )
    # ).output
    print(f"[DEBUG]response:{response}")
    res = response['choices'][0]['message']['content']
    # token_usage = response['usage']['total_tokens']
    # logger.log(token_usage)
    return res
