import asyncio
import json
import os
import time

import aiohttp
import openai

SECONDS_TO_PAUSE_AFTER_RATE_LIMIT_ERROR = 15
MAX_REQUESTS_PER_MINUTE = 100
MAX_TOKENS_PER_MINUTE = 35000

from collections import deque

from aiohttp_socks import ProxyConnector  # type: ignore


class RateLimiter:

    def __init__(self, max_rate, max_tokens_per_minute):
        self.max_rate = max_rate
        self.max_tokens_per_minute = max_tokens_per_minute
        self.start_time = time.time()
        self.request_count = 0
        self.token_usage = deque()

    async def wait(self):
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
        self.token_usage.append((tokens, time.time()))


async def fetch(
    session, url, headers, payload, rate_limiter, pbar=None, logit_bias=None
):
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
            else:
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
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openai.api_key}",
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
