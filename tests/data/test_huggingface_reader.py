from unittest.mock import patch

from yival.data.huggingface_dataset_reader import (
    HuggingFaceDatasetReader,
    HuggingFaceDatasetReaderConfig,
    InputData,
)

# Mock response data
fake_response_data = {
    'rows': [{
        'row': {
            'question': 'What is 2+2?',
            'answer': '4'
        }
    }, {
        'row': {
            'question': 'What is 3+3?',
            'answer': '6'
        }
    }]
}


# Mock requests.get
@patch('requests.get')
def test_read_method(mock_get):
    # Setup
    mock_get.return_value.json.return_value = fake_response_data
    reader_config = HuggingFaceDatasetReaderConfig(
        chunk_size=1000,
        example_limit=2,
        output_mapping={'question': 'transformed_question'},
        include=['.*'],
        exclude=[]
    )
    reader = HuggingFaceDatasetReader(reader_config)

    # Act
    result = list(reader.read("some_path"))[0]

    # Assert
    assert len(result) == 2
    assert isinstance(result[0], InputData)
    assert result[0].content == {'transformed_question': 'What is 2+2?'}
