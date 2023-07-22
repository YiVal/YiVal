from dataclasses import dataclass
from enum import Enum
from typing import Callable, List, Type, Union

from ..data.base_reader import BaseReader
from .reader_configs import BaseReaderConfig


class DatasetSourceType(Enum):
    """
    Enum to specify the source of dataset: USER, DATASET, or MACHINE_GENERATED.
    """

    USER = "user_input"
    DATASET = "dataset"
    MACHINE_GENERATED = "machine_generated"


@dataclass
class Reader:
    """
    Configuration for the reader used in the experiment.
    """

    reader_config: BaseReaderConfig  # Configuration for the reader
    reader: Type[BaseReader]  # Class reference to the reader type


@dataclass
class DatasetConfig:
    """
    Configuration for the dataset used in the experiment.

    Attributes:
    - source_type (DatasetSourceType): Source of dataset, either directly from the user,
      from a dataset, or machine-generated.
    - file_path (Union[str, None]): Path to the dataset file. Relevant only if
      source_type is DATASET.
    - reader (Union[Callable, None]): Callable to read and process the dataset file.
      Relevant only if source_type is DATASET.
    - output_path (Union[str, None]): Path to store the machine-generated data. Relevant
      only if source_type is MACHINE_GENERATED.
    - data_generators (Union[List[Callable], None]): List of callables to generate data.
      Relevant only if source_type is MACHINE_GENERATED.
    """

    source_type: DatasetSourceType
    file_path: Union[str, None] = None
    reader: Union[Callable, None] = None
    output_path: Union[str, None] = None
    data_generators: Union[List[Callable], None] = None
