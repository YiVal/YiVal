import time


class RateLimiter:

    def __init__(self, max_rate):
        self.max_rate = max_rate
        self.start_time = time.time()
        self.request_count = 0

    def __call__(self):
        self.request_count += 1
        elapsed_time = time.time() - self.start_time
        expected_time = self.request_count / self.max_rate
        if elapsed_time < expected_time:
            time.sleep(expected_time - elapsed_time)
