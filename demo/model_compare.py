import os

from openai import OpenAI

from yival.logger.token_logger import TokenLogger
from yival.schemas.experiment_config import MultimodalOutput
from yival.schemas.model_configs import Request
from yival.states.experiment_state import ExperimentState
from yival.wrappers.string_wrapper import StringWrapper


def model_compare(input: str, state: ExperimentState) -> MultimodalOutput:
    logger = TokenLogger()
    logger.reset()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model=str(
            StringWrapper("gpt-3.5-turbo", name="model_name", state=state)
        ),
        messages=[{
            "role": "user",
            "content": input
        }]
    )

    res = MultimodalOutput(text_output=response.choices[0].message.content)
    if response.usage is not None:
        token_usage = response.usage.total_tokens
    else:
        token_usage = 0
    logger.log(token_usage)
    return res


def main():
    print(
        model_compare(
            "Generate one landing page headline for AI startup company, headline only and nothing else"
        )
    )


if __name__ == "__main__":
    main()
