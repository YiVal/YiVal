import threading
from collections import defaultdict


class ExperimentState:
    """
    Represents the global experiment state for managing and rotating experiment
    variations.
    This singleton class maintains the state of active experiments, their variations,
    counters for each
    variation to ensure rotation, and locks for thread-safe access.
    Attributes:
        active (bool): Indicates if the experiment is currently active.
        current_variations (dict): A dictionary where keys are experiment names and
        values are lists of variations.
        counters (defaultdict[int]): A counter for each experiment name to rotat
        e through its variations.
        locks (defaultdict[threading.Lock]): A thread lock for each experiment name
        ensuring thread-safe access.
    Methods:
        get_next_variation(name: str) -> str:
            Retrieves the next variation for the given experiment name, rotating
            through the list of variations.
            If there are no variations for the given name, it returns None.

    Note:
        The class is designed as a singleton, ensuring a consistent global state
        throughout the application.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.active = False
            self.current_variations = {}
            self.counters = defaultdict(int)
            self.locks = defaultdict(threading.Lock)
            self.initialized = True

    def get_next_variation(self, name):
        """
        Retrieves the next variation for the given experiment name.

        This method ensures a rotation through the list of variations associated with
        the given experiment name.
        It uses a counter to determine the next variation and increments the counter
        after each retrieval.
        If there are no variations associated with the given name, it returns None.

        Thread safety is ensured through locks, allowing for concurrent access without
        race conditions.

        Parameters:
        - name (str): The name of the experiment for which to retrieve the next
        variation.

        Returns:
        - str: The next variation for the given experiment name. If there are no
        variations, returns None.
        """
        with self.locks[name]:
            variations = self.current_variations.get(name, [])
            if variations:
                index = self.counters[name] % len(variations)
                self.counters[name] += 1
                return variations[index]
            return None
