from typing import Iterator, List

from ..data.base_reader import BaseReader
from ..schemas.common_structures import InputData
from ..schemas.dataset_config import DatasetConfig, DatasetSourceType


class DataProcessor:
    """
    Utility class to process data based on DatasetConfig.
    """

    def __init__(self, config: DatasetConfig):
        self.config = config

    def process_data(self) -> Iterator[List[InputData]]:
        """
        Processes data based on the DatasetConfig and returns the processed data.
        """

        # If the source type is a dataset, use a reader to process it
        if self.config.source_type == DatasetSourceType.DATASET:
            return self._process_dataset()

        # If the source type is machine-generated, use data generators
        elif self.config.source_type == DatasetSourceType.MACHINE_GENERATED:
            return self._process_machine_generated()

        # If the source type is user input, process the user input
        elif self.config.source_type == DatasetSourceType.USER:
            return self._process_user_input()

        else:
            raise ValueError(
                f"Unknown source type: {self.config['source_type']}"
            )

    def _process_dataset(self) -> Iterator[List[InputData]]:
        """
        Processes data from a dataset.
        """

        if not self.config.reader or not self.config.file_path:
            return iter([])  # return empty iterator

        # Instantiate the reader based on the config's reader attribute
        if self.config.reader:
            reader_cls = BaseReader.get_reader(self.config.reader)
            if reader_cls:
                config_cls = BaseReader.get_config_class(self.config.reader)
                if config_cls and self.config.reader_config:
                    config_instance = config_cls(
                        **self.config.reader_config.asdict()
                    )
                reader = reader_cls(config_instance)
                return reader.read(self.config.file_path)
        return iter([])

    def _process_machine_generated(self) -> Iterator[List[InputData]]:
        """
        Processes machine-generated data.
        """
        # Implement logic for processing machine-generated data
        return iter([])

    def _process_user_input(self) -> Iterator[List[InputData]]:
        """
        Processes user input data.
        """
        # Implement logic for processing user input data
        return iter([])
