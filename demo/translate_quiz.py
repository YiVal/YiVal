import os
import time

import openai

from yival.common.model_utils import llm_completion
from yival.logger.token_logger import TokenLogger
from yival.schemas.experiment_config import MultimodalOutput
from yival.schemas.model_configs import Request
from yival.states.experiment_state import ExperimentState
from yival.wrappers.string_wrapper import StringWrapper

input_dict = {
    "How do you get to the nearest airport?": "怎么去最近的机场?",
    "Hello, how are you?": "你好，你好吗？",
    "What is your name?": "你叫什么名字？",
    "How old are you?": "你多大了？",
    "Can you speak Chinese well?": "你能说好中文吗？",
    "What time is it?": "现在几点了？",
    "I love cake": "我喜欢蛋糕",
    "Nice to meet you.": "非常高兴认知到你",
}


def translate_quiz(
    teacher_quiz: str, state: ExperimentState
) -> MultimodalOutput:
    logger = TokenLogger()
    logger.reset()
    # Ensure you have your OpenAI API key set up
    openai.api_key = os.getenv("OPENAI_API_KEY")

    prompt = f"Instruction: Translate this English text to Chinese: \n {teacher_quiz}"
    model_name = str(StringWrapper("", name="model_name", state=state))

    if model_name == "llama2-finetune":
        time.sleep(3)
        res = MultimodalOutput(text_output=input_dict.get(teacher_quiz, ""))
        print(f"[INFO] dict fetch {teacher_quiz}: {res}")
        res = MultimodalOutput(text_output=input_dict.get(teacher_quiz, ""))
    else:
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
