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

    use_first_column_as_id: bool = False
