from dataclasses import dataclass


@dataclass
class BaseReaderConfig:
    """
    Base configuration class for all readers.
    """

    chunk_size: int = 100


@dataclass
class CSVReaderConfig(BaseReaderConfig):
    """
    Configuration specific to the CSV reader.
    """

    pass
