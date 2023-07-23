from typing import Iterator, List

import pytest

from ..schemas.common_structures import InputData
from ..schemas.reader_configs import BaseReaderConfig
from .base_reader import BaseReader


# Mocking a concrete implementation of BaseReader for testing purposes
class MockReader(BaseReader):

    def read(self, path: str) -> Iterator[List[InputData]]:
        yield [InputData(example_id="123", content={})]


@pytest.fixture
def mock_reader():
    config = BaseReaderConfig()
    return MockReader(config)


def test_generate_example_id_default(mock_reader):
    row_data = {"field1": "value1", "field2": "value2"}
    path = "test_path"

    # Generating example_id
    example_id = mock_reader.generate_example_id(row_data, path)

    # Ensure that the generated ID contains the path
    assert path in example_id

    # If you have a specific format in mind for the ID, you can test it here
    # For this example, I'm assuming a format like "test_path_hash_somehashvalue"
    assert example_id.startswith(f"{path}")
