import os

from openai import OpenAI

from yival.logger.token_logger import TokenLogger
from yival.schemas.experiment_config import MultimodalOutput
from yival.states.experiment_state import ExperimentState
from yival.wrappers.string_wrapper import StringWrapper


def summarize(article: str, state: ExperimentState) -> MultimodalOutput:
    logger = TokenLogger()
    logger.reset()
    # Ensure you have your OpenAI API key set up
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Use the chat-based completion
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{
            "role":
            "system",
            "content":
            str(
                StringWrapper(
                    "You will be given an article, summarize it",
                    name="summarization",
                    state=state
                )
            )
        }, {
            "role": "user",
            "content": article
        }]
    )

    answer = MultimodalOutput(
        text_output=response.choices[0].message.content,
    )
    if response.usage is not None:
        token_usage = response.usage.total_tokens
    else:
        token_usage = 0
    logger.log(token_usage)

    return answer
