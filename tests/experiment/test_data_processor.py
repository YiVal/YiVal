from unittest.mock import MagicMock, patch

import pytest

from yival.experiment.data_processor import DataProcessor, DatasetSourceType

DATASET_CONFIG = {
    "source_type": DatasetSourceType.DATASET.value,
    "reader": "sample_reader",
    "file_path": "sample_path",
    "reader_config": {
        "some_key": "some_value"
    }
}

MACHINE_GENERATED_CONFIG = {
    "source_type": DatasetSourceType.MACHINE_GENERATED.value,
    "data_generators": {
        "sample_generator": {
            "some_key": "some_value"
        }
    }
}


class MockReader:

    def __init__(self, config):
        pass

    def read(self, file_path):
        yield ["sample_data"]


class MockGenerator:

    def __init__(self, config):
        pass

    def generate_examples(self):
        yield ["generated_data"]


def test_process_data_with_dataset():
    processor = DataProcessor(DATASET_CONFIG)
    with patch(
        'yival.data.base_reader.BaseReader.get_reader',
        return_value=MockReader
    ):
        result = next(processor.process_data(), None)
        assert result == ["sample_data"]


def test_process_data_with_machine_generated():
    processor = DataProcessor(MACHINE_GENERATED_CONFIG)

    with patch('yival.data_generators.base_data_generator.BaseDataGenerator.get_data_generator', return_value=MockGenerator), \
         patch('yival.data_generators.base_data_generator.BaseDataGenerator.get_config_class', return_value=MagicMock):

        result = next(processor.process_data(), None)
        assert result == ["generated_data"]


def test_process_data_with_unknown_source():
    config = {"source_type": "UNKNOWN"}
    processor = DataProcessor(config)
    with pytest.raises(ValueError):
        next(processor.process_data())


def test_process_dataset_with_valid_reader():
    processor = DataProcessor(DATASET_CONFIG)
    with patch(
        'yival.data.base_reader.BaseReader.get_reader',
        return_value=MockReader
    ):
        result = next(processor._process_dataset(), None)
        assert result == ["sample_data"]


def test_process_dataset_with_invalid_reader():
    config = {
        "source_type": DatasetSourceType.DATASET.value,
        "file_path": "sample_path"
    }
    processor = DataProcessor(config)
    result = next(processor._process_dataset(), None)
    assert result is None


def test_process_machine_generated_with_valid_generator():
    processor = DataProcessor(MACHINE_GENERATED_CONFIG)

    with patch('yival.data_generators.base_data_generator.BaseDataGenerator.get_data_generator', return_value=MockGenerator), \
         patch('yival.data_generators.base_data_generator.BaseDataGenerator.get_config_class', return_value=MagicMock):

        result = next(processor._process_machine_generated(), None)
        assert result == ["generated_data"]


def test_process_machine_generated_with_invalid_generator():
    config = {"source_type": DatasetSourceType.MACHINE_GENERATED.value}
    processor = DataProcessor(config)
    result = next(processor._process_machine_generated(), None)
    assert result is None
