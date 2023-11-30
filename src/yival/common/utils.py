"""
Common util funtions.
"""
import asyncio
import json
import os
import time
from collections import deque

import aiohttp
import openai
import requests
from aiohttp_socks import ProxyConnector  # type: ignore

SECONDS_TO_PAUSE_AFTER_RATE_LIMIT_ERROR = 15
MAX_REQUESTS_PER_MINUTE = 100
MAX_TOKENS_PER_MINUTE = 35000


class RateLimiter:
    """
    A rate limiter that ensures requests don't exceed a given rate and token
    usage.

    The rate limiter checks two conditions:
    1. The rate at which requests are being made.
    2. The number of tokens being used per minute.

    Attributes:
        max_rate (int): Maximum number of requests allowed per second.
        max_tokens_per_minute (int): Maximum number of tokens allowed to be
                                    used per minute.
        start_time (float): The start time when the rate limiter was
                            initialized.
        request_count (int): Number of requests made since the rate limiter
                            was initialized.
        token_usage (deque): A deque containing tuples of tokens used and the
                            time they were used at.
    """

    def __init__(self, max_rate, max_tokens_per_minute):
        """
        Initialize the rate limiter with maximum rate and tokens per minute.

        Args:
            max_rate (int): Maximum number of requests allowed per second.
            max_tokens_per_minute (int): Maximum number of tokens allowed to
                                        be used per minute.
        """
        self.max_rate = max_rate
        self.max_tokens_per_minute = max_tokens_per_minute
        self.start_time = time.time()
        self.request_count = 0
        self.token_usage = deque()

    async def wait(self):
        """
        Wait until it's safe to make another request based on the rate and
        token limits.

        This method calculates the expected time for the next request and
        waits if necessary.
        It also ensures that the token usage does not exceed the specified
        limit.
        """
        self.request_count += 1
        elapsed_time = time.time() - self.start_time
        expected_time = self.request_count / self.max_rate
        sleep_time = max(expected_time - elapsed_time, 0)
        await asyncio.sleep(sleep_time)

        # Check if tokens used more than a minute ago, and remove them
        while self.token_usage and self.token_usage[0][1] < time.time() - 60:
            self.token_usage.popleft()

        # Check if the current token count exceeds the limit
        current_tokens = sum(token for token, _ in self.token_usage)
        while current_tokens >= self.max_tokens_per_minute:
            await asyncio.sleep(1)  # Wait a second and check again
            while self.token_usage and self.token_usage[0][1] < time.time(
            ) - 60:
                self.token_usage.popleft()
            current_tokens = sum(token for token, _ in self.token_usage)

    def add_tokens(self, tokens):
        """
        Add tokens to the token usage queue.

        Args:
            tokens (int): Number of tokens to be added.
        """
        self.token_usage.append((tokens, time.time()))


async def fetch(
    session, url, headers, payload, rate_limiter, pbar=None, logit_bias=None
):
    """
    Asynchronous function to fetch data using POST request with retries for
    rate limits.

    Args:
        session (aiohttp.ClientSession): The session to make the request.
        url (str): The URL endpoint to fetch from.
        headers (dict): Headers to include in the request.
        payload (dict): Data payload to send with the request.
        rate_limiter (RateLimiter): An instance of RateLimiter to control the
                                    request rate.
        pbar (optional): A progress bar instance to show progress. Defaults to
                        None.
        logit_bias (optional): Bias for the logit. Defaults to None.

    Returns:
        dict: The response data if the request was successful.
    """
    while True:
        await rate_limiter.wait()  # Wait for the rate limiter

        if logit_bias:
            payload['logit_bias'] = logit_bias

        async with session.post(
            url, headers=headers, data=json.dumps(payload)
        ) as response:
            response_data = await response.json()
            if response.status == 429:  # Rate limit exceeded
                print("Rate limit exceeded, sleeping...")
                await asyncio.sleep(SECONDS_TO_PAUSE_AFTER_RATE_LIMIT_ERROR)
                continue  # Retry the request

            choices = response_data.get('choices')
            total_tokens = response_data.get('usage',
                                             {}).get('total_tokens', 0)
            rate_limiter.add_tokens(
                total_tokens
            )  # Add the tokens used to the rate limiter

            if choices and len(choices) > 0 and choices[0]:
                if pbar:
                    pbar.update(1)
                return response_data

            print(f"Invalid choices in response. Choices: {choices}")

        print("Response criteria not met, retrying...")
        continue


async def parallel_completions(
    message_batches,
    model,
    max_tokens,
    temperature=1.3,
    presence_penalty=0,
    pbar=None,
    logit_bias=None
):
    """
    Asynchronous function to perform parallel completions using OpenAI's API.

    Args:
        message_batches (list): A list containing batches of messages for
                                completion.
        model (str): The model to be used for completion.
        max_tokens (int): Maximum tokens to be used for completion.
        temperature (float, optional): Sampling temperature. Defaults to 1.3.
        presence_penalty (float, optional): Presence penalty for completion.
                                            Defaults to 0.
        pbar (optional): A progress bar instance to show progress. Defaults to
                        None.
        logit_bias (optional): Bias for the logit. Defaults to None.

    Returns:
        list: A list of responses containing completions for each message
            batch.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    rate_limiter = RateLimiter(
        MAX_REQUESTS_PER_MINUTE / 60, MAX_TOKENS_PER_MINUTE
    )  # Create a rate limiter

    proxy = os.environ.get("all_proxy")
    if proxy:
        connector = ProxyConnector.from_url(proxy)
    else:
        connector = None

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [
            asyncio.ensure_future(
                fetch(
                    session, url, headers, {
                        "model": model,
                        "messages": messages,
                        "temperature": temperature,
                        "presence_penalty": presence_penalty,
                        "max_tokens": max_tokens
                    }, rate_limiter, pbar, logit_bias
                )
            ) for messages in message_batches
        ]

        responses = await asyncio.gather(*tasks)

    return responses


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
    }

    # Send the POST request with the payload
    response = requests.post(url, json=payload, headers=headers)

    # Return the response object
    return response.json()["id"]


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


def create_assistant_and_get_response(input_message, assistant_id):
    # Helper function to check run status and wait until it is completed
    def wait_for_run_completion(thread_id, run_id):
        while True:
            if check_run_status(thread_id, run_id):
                break  # Exit the loop if the run is completed
            time.sleep(
                1
            )  # Sleep for some time before checking again to avoid rate limiting

    # Reuse the previous functions, modifying them if necessary for the current context

    # Assuming create_thread(), post_message_to_thread(), create_run(), check_run_status(), and list_messages() are already defined

    # Start the workflow
    thread_id = create_thread()
    post_message_to_thread(thread_id, input_message)
    run_id = create_run(thread_id, assistant_id)
    wait_for_run_completion(thread_id, run_id)  # Wait for the run to complete
    messages = list_messages(thread_id)  # Retrieve the list of messages
    return messages['data'][0]['content'][0]['text']['value']


def check_run_status(thread_id, run_id) -> bool:
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
        return status == "completed" or status == "failed" or status == "queued"
    else:
        # Handle different status codes or provide more detailed error information here if necessary
        return False
