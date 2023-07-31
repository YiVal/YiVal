from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

from .data_generator_configs import BaseDataGeneratorConfig
from .reader_configs import BaseReaderConfig


class DatasetSourceType(Enum):
    """
    Enum to specify the source of dataset: USER, DATASET, or MACHINE_GENERATED.
    """

    USER = "user_input"
    DATASET = "dataset"
    MACHINE_GENERATED = "machine_generated"


@dataclass
class DatasetConfig:
    """
    Configuration for the dataset used in the experiment.

    Attributes:
    - source_type (DatasetSourceType): Source of dataset, either directly from the user,
      from a dataset, or machine-generated.
    - file_path (Union[str, None]): Path to the dataset file. Relevant only if
      source_type is DATASET.
    - reader (Union[str, None]): Class name to process the dataset file.
      Relevant only if source_type is DATASET.
    - reader_config (Union[BaseReaderConfig, None]): Configuration for the reader.
    - output_path (Union[str, None]): Path to store the machine-generated data. Relevant
      only if source_type is MACHINE_GENERATED.
    - data_generators (Optional[Dict[str, BaseDataGeneratorConfig]]): List of data_generators to generate data.
      Relevant only if source_type is MACHINE_GENERATED.
    """

    source_type: DatasetSourceType
    file_path: Optional[str] = None
    reader: Optional[str] = None
    reader_config: Optional[BaseReaderConfig] = None
    output_path: Optional[str] = None
    data_generators: Optional[Dict[str, BaseDataGeneratorConfig]] = None

    def asdict(self) -> Dict[str, Any]:
        return {
            "source_type":
            str(self.source_type),
            "file_path":
            self.file_path,
            "reader":
            self.reader,
            "reader_config":
            self.reader_config.asdict() if self.reader_config else None,
            "output_path":
            self.output_path,
            "data_generators": {
                k: v.asdict()
                for k, v in self.data_generators.items()
            } if self.data_generators else None
        }
