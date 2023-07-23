from typing import Dict, List, Type


class BaseParserWithRegistry:
    """
    Base class for parsers that provides automatic registration of subclasses.
    Any subclass that inherits from this base class will be automatically added
    to the registry. The registry can then be used to retrieve a parser class
    based on its name.
    """

    registry: Dict[str, Type["BaseParserWithRegistry"]] = {
    }  # Class-level registry for all parser subclasses

    def __init_subclass__(cls, **kwargs):
        """Automatically called when a subclass is defined."""
        super().__init_subclass__(**kwargs)
        # Register the subclass in the registry using its name
        BaseParserWithRegistry.registry[cls.__name__] = cls

    def parse(self, output: str) -> List[str]:
        """
        Parse the provided output.
        This method should be overridden by subclasses to provide custom parsing logic.
        """
        raise NotImplementedError("Subclasses must override the parse method.")
