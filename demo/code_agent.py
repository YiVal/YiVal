import os
import re
import time

import autogen
import requests
import tiktoken

from yival.logger.token_logger import TokenLogger
from yival.schemas.experiment_config import MultimodalOutput
from yival.states.experiment_state import ExperimentState
from yival.wrappers.string_wrapper import StringWrapper


def num_tokens_from_string(
    string: str, encoding_name: str = "cl100k_base"
) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def concat_conversation_content(data):
    # This will hold the concatenated string of all contents
    all_content = ""

    # Iterate over the conversation entries
    for entry in data.values():
        # Each entry is a list of messages
        for message in entry:
            # Concatenate content with a space to separate each message
            all_content += message['content'] + " "

    # Strip any leading/trailing whitespace
    all_content = all_content.strip()

    return all_content


def extract_python_code(data):
    code_snippets = []

    for entry in data.values():
        # Each entry is a list of messages
        for message in entry:
            if '```python' in message['content']:
                # Extract the code between the ```python markers
                start = message['content'].find('```python') + len('```python')
                end = message['content'].find('```', start)
                code = message['content'][start:end].strip()
                code_snippets.append(code)

    return code_snippets[-1]


def create_assistant(name, tools, model, instructions):
    """
    Send a request to create an assistant with the specified parameters.
    
    :param name: Name of the assistant.
    :param tools: List of tools to be used by the assistant.
    :param model: Model version of the assistant.
    :param instructions: Role of the assistant.
    :param api_key: API key for authorization.
    :return: Response from the API.
    """
    # URL for the API endpoint
    url = "https://api.openai.com/v1/assistants"
    api_key = os.getenv("OPENAI_API_KEY")

    # Headers to be sent with the request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "OpenAI-Beta": "assistants=v1"
    }

    # Data payload for creating the assistant
    payload = {
        "name": name,
        "tools": tools,
        "model": model,
        "instructions": instructions
    }

    # Send the POST request
    response = requests.post(url, json=payload, headers=headers)
    # Return the response object
    return response.json()["id"]


def create_thread():
    """
    Send a request to the OpenAI API to create a thread.

    :param api_key: API key for authorization.
    :return: Response from the API.
    """
    # URL for the API endpoint to create threads
    url = "https://api.openai.com/v1/threads"

    api_key = os.getenv("OPENAI_API_KEY")

    # Headers to be sent with the request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "OpenAI-Beta": "assistants=v1"
    }

    # Send the POST request with an empty data payload
    response = requests.post(url, headers=headers, data='')

    # Return the response object
    return response.json()["id"]


def check_run_status(thread_id, run_id):
    """
    Check the status of a run within a thread on the OpenAI API.

    :param thread_id: The identifier of the thread.
    :param run_id: The identifier of the run.
    :return: True if the status is 'completed', False otherwise.
    """
    # Retrieve the API key from an environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("The OPENAI_API_KEY environment variable is not set.")

    # URL for the API endpoint to get the status of a run within a thread
    url = f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}"

    # Headers to be sent with the request
    headers = {
        "Authorization": f"Bearer {api_key}",
        "OpenAI-Beta": "assistants=v1"
    }

    # Send the GET request
    response = requests.get(url, headers=headers)

    # Check if the response status code is 200 and if the status in the response JSON is 'completed'
    if response.status_code == 200:
        status = response.json().get('status')
        return status == "completed"
    else:
        # Handle different status codes or provide more detailed error information here if necessary
        return False


def create_run(thread_id, assistant_id):
    """
    Start a run for an assistant in a specific thread on the OpenAI API.

    :param thread_id: The identifier of the thread.
    :param assistant_id: The identifier of the assistant.
    :return: Response from the API.
    """
    # Retrieve the API key from an environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("The OPENAI_API_KEY environment variable is not set.")

    # URL for the API endpoint to create a run within a thread
    url = f"https://api.openai.com/v1/threads/{thread_id}/runs"

    # Headers to be sent with the request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "OpenAI-Beta": "assistants=v1"
    }

    # Data payload for creating the run
    payload = {
        "assistant_id": assistant_id,
        "instructions": "Return the python code only"
    }

    # Send the POST request with the payload
    response = requests.post(url, json=payload, headers=headers)

    # Return the response object
    return response.json()["id"]


def post_message_to_thread(thread_id, content):
    """
    Send a message to a specific thread on the OpenAI API.

    :param thread_id: The identifier of the thread.
    :param content: The content of the message to be sent.
    :return: Response from the API.
    """
    # Retrieve the API key from an environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("The OPENAI_API_KEY environment variable is not set.")

    # URL for the API endpoint to post a message to a thread
    url = f"https://api.openai.com/v1/threads/{thread_id}/messages"

    # Headers to be sent with the request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "OpenAI-Beta": "assistants=v1"
    }

    # Data payload for the message
    payload = {"role": "user", "content": content}

    # Send the POST request with the message data payload
    response = requests.post(url, json=payload, headers=headers)

    # Return the response object
    return response


termination_msg = lambda x: isinstance(x, dict) and "TERMINATE" == str(
    x.get("content", "")
)[-9:].upper()


def auto_gen_code(problem):
    config_list_gpt4 = autogen.config_list_from_json(
        "OAI_CONFIG_LIST",
        filter_dict={
            "model": [
                "gpt-4", "gpt-4-0314", "gpt4", "gpt-4-32k", "gpt-4-32k-0314",
                "gpt-4-32k-v0314"
            ],
        },
    )
    gpt4_config = {
        "seed": 42,  # change the seed for different trials
        "temperature": 0,
        "config_list": config_list_gpt4,
        "timeout": 300,
    }
    user_proxy = autogen.UserProxyAgent(
        name="Admin",
        system_message=
        "A human admin. Interact with the Engineer to discuss the algorithm and code. Double check algorithm and make sure time complexity is optimal. If not optimal, ask enginner to revise",
        code_execution_config=False,
        llm_config=gpt4_config,
        is_termination_msg=termination_msg,
        human_input_mode="NEVER"
    )
    engineer = autogen.AssistantAgent(
        name="Engineer",
        llm_config=gpt4_config,
        system_message=
        '''Engineer. You write python/shell code to solve tasks. Analysis the time complexity first and make sure it is optimal, Wrap the code in a code block that specifies the script type. The user can't modify your code. So do not suggest incomplete code which requires others to modify. Don't use a code block if it's not intended to be executed by the executor.
    Don't include multiple code blocks in one response. Output the test case and the code in same python code block. Do not add any word in between. Do not ask others to copy and paste the result. Check the execution result returned by the executor.
    If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
    Ask admin to double check algorithm and time complexity.
    For example 
    ```python
    def abc ():
        print("abc")
    ```
    and 
    Let's test this function 
     ```python
     abc()
    ```
    should become
    ```python
    def abc ():
        print("abc")
    
    abc()
    ```
    Reply `TERMINATE` in the end when everything is done
    ''',
    )
    executor = autogen.UserProxyAgent(
        name="Executor",
        system_message=
        "Executor. Execute the code written by the engineer and report the result.",
        human_input_mode="NEVER",
        code_execution_config={
            "last_n_messages": 3,
            "work_dir": "paper"
        },
    )

    groupchat = autogen.GroupChat(
        agents=[user_proxy, executor, engineer], messages=[], max_round=10
    )
    manager = autogen.GroupChatManager(
        groupchat=groupchat, llm_config=gpt4_config
    )

    # the assistant receives a message from the user_proxy, which contains the task description
    user_proxy.initiate_chat(
        manager,
        message=problem,
    )
    return user_proxy.chat_messages


def list_messages(thread_id):
    """
    List messages in a specific thread on the OpenAI API.

    :param thread_id: The identifier of the thread.
    :return: Response from the API.
    """
    # Retrieve the API key from an environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("The OPENAI_API_KEY environment variable is not set.")

    # URL for the API endpoint to list messages in a thread
    url = f"https://api.openai.com/v1/threads/{thread_id}/messages"

    # Headers to be sent with the request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "OpenAI-Beta": "assistants=v1"
    }

    # Send the GET request
    response = requests.get(url, headers=headers)

    # Return the response object
    return response.json()


def process_messages(response: dict):
    """
    Process the list messages response to count tokens and extract Python code.

    :param response: The list messages API response.
    :return: A tuple containing the token count and the latest Python code block.
    """
    token_count = 0
    latest_python_code = ""

    # Concatenate all text to count tokens
    concatenated_text = ""
    for message in response['data']:
        for content in message['content']:
            if content['type'] == 'text':
                concatenated_text += content['text']['value'] + "\n"

    # Count the tokens
    token_count = num_tokens_from_string(concatenated_text)

    # Extract the latest Python code block
    for message in reversed(response['data']):  # Start from the latest message
        for content in message['content']:
            if content['type'] == 'text':
                text_value = content['text']['value']
                match = re.search(r'```python(.*?)```', text_value, re.DOTALL)
                if match:
                    latest_python_code = match.group(1).strip()
                    break  # Stop after finding the latest Python code block
        if latest_python_code:  # If we found a code block, no need to continue
            break

    return token_count, latest_python_code


def create_assistant_and_get_response(input_message, assistant_id):
    # Helper function to check run status and wait until it is completed
    def wait_for_run_completion(thread_id, run_id):
        while True:
            if check_run_status(thread_id, run_id):
                break  # Exit the loop if the run is completed
            time.sleep(
                3
            )  # Sleep for some time before checking again to avoid rate limiting

    # Reuse the previous functions, modifying them if necessary for the current context

    # Assuming create_thread(), post_message_to_thread(), create_run(), check_run_status(), and list_messages() are already defined

    # Start the workflow
    thread_id = create_thread()
    post_message_to_thread(thread_id, input_message)
    run_id = create_run(thread_id, assistant_id)
    wait_for_run_completion(thread_id, run_id)  # Wait for the run to complete
    messages = list_messages(thread_id)  # Retrieve the list of messages
    token_count, latest_python_code = process_messages(messages)
    return token_count, latest_python_code


def run_leetcode(
    leetcode_problem: str, state: ExperimentState
) -> MultimodalOutput:
    logger = TokenLogger()
    logger.reset()
    # Ensure you have your OpenAI API key set up
    use_autogen = StringWrapper("use_autogen", name="use_autogen", state=state)
    if str(use_autogen) == "use_autogen":
        auto_gen_problem = auto_gen_code(leetcode_problem)
        code = extract_python_code(auto_gen_code(leetcode_problem))
        logger.log(
            num_tokens_from_string(
                concat_conversation_content(auto_gen_problem)
            )
        )
        return MultimodalOutput(text_output=code)

    else:
        assistant_id = create_assistant(
            name="Senior software Engineer",
            instructions=
            "You are a senior software engineer. Solve leetcode problem using your coding and language skills with python. return python code",
            tools=[{
                "type": "code_interpreter"
            }],
            model="gpt-4-1106-preview"
        )
        token_count, code = create_assistant_and_get_response(
            leetcode_problem, assistant_id
        )
        logger.log(token_count)
        # print(token_count)
        return MultimodalOutput(text_output=code)
