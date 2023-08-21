from typing import Any, Iterator, List

from ..data.base_reader import BaseReader
from ..data_generators.base_data_generator import BaseDataGenerator
from ..schemas.common_structures import InputData
from ..schemas.data_generator_configs import BaseDataGeneratorConfig
from ..schemas.dataset_config import DatasetConfig, DatasetSourceType
from ..schemas.reader_configs import BaseReaderConfig


class DataProcessor:
    """
    Utility class to process data based on DatasetConfig.
    """

    def __init__(self, config: Any):
        self.config = DatasetConfig(**config)

    def process_data(self) -> Iterator[List[InputData]]:
        """
        Processes data based on the DatasetConfig and returns the processed
        data.
        """

        # If the source type is a dataset, use a reader to process it
        if self.config.source_type == DatasetSourceType.DATASET.value:
            return self._process_dataset()

        # If the source type is machine-generated, use data generators
        elif self.config.source_type == DatasetSourceType.MACHINE_GENERATED.value:
            return self._process_machine_generated()

        else:
            raise ValueError(f"Unknown source type: {self.config.source_type}")

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
                if config_cls:
                    if self.config.reader_config:
                        if isinstance(self.config.reader_config, dict):
                            config_data = self.config.reader_config
                        else:
                            config_data = self.config.reader_config.asdict()
                        config_instance = config_cls(**config_data)
                    else:
                        config_instance = config_cls()
                    reader = reader_cls(config_instance)
                    return reader.read(self.config.file_path)
                else:
                    reader = reader_cls(BaseReaderConfig())
                    return reader.read(self.config.file_path)
        return iter([])

    def _process_machine_generated(self) -> Iterator[List[InputData]]:
        """
        Processes machine-generated data.
        """
        if self.config.data_generators:
            for data_generator, data_generator_config in self.config.data_generators.items(
            ):
                data_generator_cls = BaseDataGenerator.get_data_generator(
                    data_generator
                )
                if data_generator_cls:
                    config_cls = BaseDataGenerator.get_config_class(
                        data_generator
                    )
                    if config_cls:
                        if isinstance(data_generator_config, dict):
                            config_data = data_generator_config
                        else:
                            config_data = data_generator_config.asdict()
                        config_instance = config_cls(**config_data)
                        data_generator_instance = data_generator_cls(
                            config_instance
                        )
                        return data_generator_instance.generate_examples()
                    else:
                        data_generator_instance = data_generator_cls(
                            BaseDataGeneratorConfig()
                        )

        # Implement logic for processing machine-generated data
        return iter([])
