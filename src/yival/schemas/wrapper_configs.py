from dataclasses import asdict, dataclass


@dataclass
class BaseWrapperConfig:
    """
    Base configuration class for wrappers.
    """

    def asdict(self):
        return asdict(self)


@dataclass
class StringWrapperConfig(BaseWrapperConfig):
    """
    Configuration specific to the StringWrapper.
    """
