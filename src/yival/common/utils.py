import asyncio
import json
import time

import aiohttp
import openai

MAX_REQUESTS_PER_MINUTE = 100
MAX_TOKENS_PER_MINUTE = 600000
SECONDS_TO_PAUSE_AFTER_RATE_LIMIT_ERROR = 15


async def fetch(session, url, headers, payload, available_tokens):
    if payload['max_tokens'] > available_tokens:
        return None  # Not enough tokens; you might want to handle this differently

    async with session.post(
        url, headers=headers, data=json.dumps(payload)
    ) as response:
        if response.status == 429:  # Rate limit exceeded
            return "rate_limit"

        return await response.json()


async def parallel_completions(message_batches, model, max_tokens):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openai.api_key}",
        "Content-Type": "application/json"
    }

    available_request_capacity = MAX_REQUESTS_PER_MINUTE
    available_token_capacity = MAX_TOKENS_PER_MINUTE
    last_update_time = time.time()

    async with aiohttp.ClientSession() as session:
        tasks = []
        for messages in message_batches:
            current_time = time.time()
            seconds_since_update = current_time - last_update_time
            available_request_capacity = min(
                available_request_capacity +
                MAX_REQUESTS_PER_MINUTE * seconds_since_update / 60.0,
                MAX_REQUESTS_PER_MINUTE,
            )
            available_token_capacity = min(
                available_token_capacity +
                MAX_TOKENS_PER_MINUTE * seconds_since_update / 60.0,
                MAX_TOKENS_PER_MINUTE,
            )
            last_update_time = current_time

            payload = {
                "model": model,
                "messages": messages,
                "temperature": 1.3,
                "presence_penalty": 2,
                "max_tokens": max_tokens
            }

            if available_request_capacity > 0 and available_token_capacity >= payload[
                'max_tokens']:
                available_request_capacity -= 1
                available_token_capacity -= payload['max_tokens']
                task = asyncio.ensure_future(
                    fetch(
                        session, url, headers, payload,
                        available_token_capacity
                    )
                )
                tasks.append(task)

            else:
                await asyncio.sleep(SECONDS_TO_PAUSE_AFTER_RATE_LIMIT_ERROR)
                last_update_time = time.time()  # Reset the last update time

        responses = await asyncio.gather(*tasks)

        # Handle rate limits and retry if necessary
        for i, response in enumerate(responses):
            if response == "rate_limit":
                await asyncio.sleep(SECONDS_TO_PAUSE_AFTER_RATE_LIMIT_ERROR)
                responses[i] = await fetch(
                    session, url, headers, message_batches[i],
                    available_token_capacity
                )

    return responses
