import os

import openai
from litellm import completion

from yival.logger.token_logger import TokenLogger
from yival.wrappers.string_wrapper import StringWrapper


def essay_topic_outline(topic: str) -> str:
    logger = TokenLogger()
    logger.reset()
    # Ensure you have your OpenAI API key set up
    openai.api_key = os.getenv("OPENAI_API_KEY")
    messages = [{
        "role":
        "system",
        "content":
        str(StringWrapper("你是一个帮助小红书博主生成标题的助手.", name="system"))
    }, {
        "role":
        "user",
        "content":
        str(StringWrapper("根据主题生成小红书标题", name="topic")) + f'{topic}'
    }]

    # Use the chat-based completion
    response = completion(
        model="gpt-3.5-turbo", messages=messages
    )
    res = response['choices'][0]['message']['content']
    token_usage = response['usage']['total_tokens']
    logger.log(token_usage)
    return res
