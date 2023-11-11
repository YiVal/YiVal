import os

from openai import OpenAI

from yival.logger.token_logger import TokenLogger
from yival.schemas.experiment_config import MultimodalOutput
from yival.states.experiment_state import ExperimentState
from yival.wrappers.string_wrapper import StringWrapper


def essay_topic_outline(
    topic: str, state: ExperimentState
) -> MultimodalOutput:
    logger = TokenLogger()
    logger.reset()
    # Ensure you have your OpenAI API key set up
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Use the chat-based completion
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role":
            "system",
            "content":
            str(
                StringWrapper(
                    "你是一个帮助小红书博主生成标题的助手.", name="system", state=state
                )
            )
        }, {
            "role":
            "user",
            "content":
            str(StringWrapper("根据主题生成小红书标题", name="topic", state=state)) +
            f'{topic}'
        }]
    )
    res = MultimodalOutput(text_output=response.choices[0].message.content)
    if response.usage is not None:
        token_usage = response.usage.total_tokens
    else:
        token_usage = 0
    logger.log(token_usage)
    return res
