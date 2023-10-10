import time

import pytest

from yival.common.utils import RateLimiter


@pytest.mark.asyncio
async def test_rate_limiter_wait():
    rate_limiter = RateLimiter(1, 35000)

    start_time = time.time()
    await rate_limiter.wait()
    elapsed_time = time.time() - start_time

    # Since the rate is set to 1 request per second, and this is the first
    # request, there shouldn't be any delay.
    assert elapsed_time < 1

    await rate_limiter.wait()
    elapsed_time = time.time() - start_time

    # Now, since it's the second request, there should be a delay close to 1
    # second.
    assert 0.9 < elapsed_time < 1.1


@pytest.mark.asyncio
async def test_rate_limiter_add_tokens():
    rate_limiter = RateLimiter(1, 35000)

    # Add tokens and check if they're correctly added
    rate_limiter.add_tokens(5000)
    total_tokens = sum(token for token, _ in rate_limiter.token_usage)
    assert total_tokens == 5000

    # Add more tokens and check the total
    rate_limiter.add_tokens(10000)
    total_tokens = sum(token for token, _ in rate_limiter.token_usage)
    assert total_tokens == 15000
