class TokenLogger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.current_usage = 0
        return cls._instance

    def log(self, tokens: int):
        self.current_usage += tokens

    def get_current_usage(self) -> int:
        """Get the token usage of the current operation."""
        return self.current_usage

    def reset(self):
        self.current_usage = 0
