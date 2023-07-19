from .base_wrapper import BaseWrapper


class StringWrapper(BaseWrapper):
    def __init__(self, original_string, name):
        super().__init__(name)
        self._original_string = original_string

    def __str__(self):
        variation = self.get_variation()
        if variation:
            return variation
        return self._original_string
