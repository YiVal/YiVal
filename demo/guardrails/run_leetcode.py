#type: ignore
import os
import re

import guardrails as gd
import openai
from guardrails.datatypes import PythonCode
from guardrails.validators import BugFreePython
from pydantic import BaseModel, Field
from rich import print

from yival.logger.token_logger import TokenLogger
from yival.states.experiment_state import ExperimentState
from yival.wrappers.string_wrapper import StringWrapper

prompt_guardrail = """
Given the following high level leetcode problem description, write a short Python code snippet that solves the problem.

Problem Description:
${leetcode_problem}

${gr.complete_json_suffix}"""

prompt_raw = """
Given the following high level leetcode problem description, write a short Python code snippet that solves the problem.

Problem Description:
${leetcode_problem}

"""


class BugFreePythonCode(BaseModel):
    python_code: PythonCode = Field(
        validators=[BugFreePython(on_fail="reask")]
    )

    class Config:
        arbitrary_types_allowed = True


async def run_leetcode(leetcode_problem: str, state: ExperimentState) -> str:
    logger = TokenLogger()
    logger.reset()
    # Ensure you have your OpenAI API key set up
    use_guardrails = StringWrapper(
        "use_guardrails", name="use_guardrails", state=state
    )
    if str(use_guardrails) == "use_guardrails":
        try:
            guard = gd.Guard.from_pydantic(
                output_class=BugFreePythonCode, prompt=prompt_guardrail
            )
            raw_llm_response, validated_response = await guard(
                llm_api=openai.ChatCompletion.acreate,
                prompt_params={"leetcode_problem": leetcode_problem},
                model="gpt-3.5-turbo",
                max_tokens=1000,
                temperature=0,
                num_reasks=3,
            )
            total_token = 0
            for log in guard.state.most_recent_call.history:
                total_token += log.llm_response.response_token_count
                total_token += log.llm_response.prompt_token_count
            logger.log(total_token)
            if validated_response and isinstance(validated_response, dict):
                return validated_response.get("python_code", "invalid")
            else:
                return "invalid"
        except Exception:
            return "guardrails throws exception"
    else:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        prompt = prompt_raw.format(leetcode_problem=leetcode_problem)
        messages = [{"role": "user", "content": prompt}]
        # Use the chat-based completion
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0,
            max_tokens=1000
        )
        res = response['choices'][0]['message']['content']
        token_usage = response['usage']['total_tokens']
        extracted_text = re.search(r'```python\n(.*?)\n```', res, re.DOTALL)
        extracted_code = extracted_text.group(1).strip(
        ) if extracted_text else None
        logger.log(token_usage)
        if extracted_code and extracted_code[0] == ' ':
            extracted_code = extracted_code[1:]
        return extracted_code


problem = """
"Given a string s, find the length of the longest substring without repeating characters.
		Example 1:
		Input: s = ""abcabcbb""
		Output: 3
		Explanation: The answer is ""abc"", with the length of 3.
		Example 2:
		Input: s = ""bbbbb""
		Output: 1
		Explanation: The answer is ""b"", with the length of 1.
		Example 3:
		Input: s = ""pwwkew""
		Output: 3
		Explanation: The answer is ""wke"", with the length of 3.
		Notice that the answer must be a substring, ""pwke"" is a subsequence and not a substring."
"""


def main():
    res = run_leetcode(problem)

    try:
        exec(res)
        print("Success!")
    except Exception:
        print("Failed!")


if __name__ == "__main__":
    main()
