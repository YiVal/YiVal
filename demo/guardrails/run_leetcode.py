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


def run_leetcode(leetcode_problem: str) -> str:
    logger = TokenLogger()
    logger.reset()
    # Ensure you have your OpenAI API key set up
    use_guardrails = StringWrapper("use_guardrails", name="use_guardrails")
    if str(use_guardrails) == "use_guardrails":
        guard = gd.Guard.from_pydantic(
            output_class=BugFreePythonCode, prompt=prompt_guardrail
        )
        raw_llm_response, validated_response = guard(
            llm_api=openai.ChatCompletion.create,
            prompt_params={"leetcode_problem": leetcode_problem},
            model="gpt-3.5-turbo",
            max_tokens=3000,
            temperature=0,
            num_reasks=3,
        )
        total_token = 0
        for log in guard.state.most_recent_call.history:
            total_token += log.llm_response.response_token_count
            total_token += log.llm_response.prompt_token_count
        print(total_token)
        logger.log(total_token)
        print(guard.state.most_recent_call.tree)
        return validated_response.get("python_code", "invalid")
    else:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        prompt = prompt_raw.format(leetcode_problem=leetcode_problem)
        messages = [{"role": "user", "content": prompt}]
        # Use the chat-based completion
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages, temperature=0
        )
        res = response['choices'][0]['message']['content']
        token_usage = response['usage']['total_tokens']
        print(token_usage)

        extracted_text = re.search(r'```python\n(.*?)\n```', res, re.DOTALL)
        extracted_code = extracted_text.group(1).strip(
        ) if extracted_text else None
        logger.log(token_usage)
        print(extracted_code)
        return extracted_code


problem = """
Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.
		You may assume that each input would have exactly one solution, and you may not use the same element twice.
		You can return the answer in any order.
		Example 1:
		Input: nums = [2,7,11,15], target = 9
		Output: [0,1]
		Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].
		Example 2:
		Input: nums = [3,2,4], target = 6
		Output: [1,2]
		Example 3:
		Input: nums = [3,3], target = 6
		Output: [0,1]
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
