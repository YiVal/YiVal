from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional


@dataclass
class BaseReaderConfig:
    """
    Base configuration class for all readers.
    """

    chunk_size: int = 100

    def asdict(self):
        return asdict(self)


@dataclass
class CSVReaderConfig(BaseReaderConfig):
    """
    Configuration specific to the CSV reader.
    """

    use_first_column_as_id: bool = False
    expected_result_column: Optional[str] = None

    def asdict(self):
        return asdict(self)


@dataclass
class HuggingFaceDatasetReaderConfig(BaseReaderConfig):
    example_limit: int = 1
    output_mapping: Dict[str, str] = field(default_factory=dict)
    # List of regex patterns to include based on content
    include: List[str] = field(default_factory=list)
    # List of regex patterns to exclude based on content
    exclude: List[str] = field(default_factory=list)
