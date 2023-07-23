from dataclasses import dataclass


@dataclass
class BaseWrapperConfig:
    """
    Base configuration class for wrappers.
    """

    pass


@dataclass
class StringWrapperConfig(BaseWrapperConfig):
    """
    Configuration specific to the StringWrapper.
    """

    pass
