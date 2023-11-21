---
sidebar_position: 3
---

# Reader

## `BaseReader`

### Introduction

  This module provides an abstract foundation for data readers. Data readers are responsible for reading data from various sources, and this module offers a base class to define and register new readers, retrieve existing ones, and fetch their configurations. The design encourages efficient parallel processing by reading data in chunks. 

### Class Definition

#### Description

#### Attributes 

### Example

### [Source Code](https://github.com/YiVal/YiVal/blob/master/src/yival/data/base_reader.py)

## `CSV Reader`

### Introduction 

  The `CSVReader` class offers a streamlined interface for reading datasets from CSV files. Built atop the BaseReader class, it provides extensive configuration options, ensures error handling, and facilitates reading data in chunks.

### Class Definition 

#### `CSVReader(BaseReader)`

##### Description

​    The `CSVReader` class, derived from `BaseReader`, is crafted to read datasets from CSV files.

##### Attributes

- **`config (CSVReaderConfig)`**: 
  - A configuration object detailing the reader's parameters.
- **`default_config (CSVReaderConfig)`**: 
  - A default configuration for the reader.

#####  Methods 

- **`__init__(self, config: CSVReaderConfig)`**:
  - Initializes the CSVReader with the provided configuration.
  - Parameters:
    - `config (CSVReaderConfig)`: The configuration object designated for the CSVReader.
- **`read(self, path: str) -> Iterator[List[InputData]]`**:
  - Reads the CSV file and yields chunks of `InputData`.
  - Parameters:
    - `path (str)`: Path pointing to the CSV file.
  - Returns: An iterator that successively yields lists of `InputData`.

#####  Notes 

- The `read` method inspects headers in the CSV file and issues an error if absent.
- Rows that lack data values are bypassed, but a log warning is recorded.
- If a column is earmarked for expected results, the method extracts those values.
- Data rows are consumed in chunks. When a chunk meets its specified size, it's yielded. The chunk size is determined by the `chunk_size` attribute in the `CSVReaderConfig`.
- The class enables registration with the BaseReader through the `register_reader` method.

#####   [Source Code ](https://github.com/YiVal/YiVal/blob/master/src/yival/data/csv_reader.py)

####  `CSVReaderConfig(BaseReaderConfig)`

#####  Description

​    The configuration object is tailored specifically for the `CSVReader` class.

##### Attributes

- **`use_first_column_as_id (bool)`**: A flag to determine if the first column should be used as an ID. The default value is `False`.
- **`expected_result_column (Optional[str])`**: Specifies the column name that contains expected results, if any. The default  value is `None`.

#####  [Source Code](https://github.com/YiVal/YiVal/blob/master/src/yival/schemas/reader_configs.py)

###  Example

   Here is a step-by-step guide on how to use `CSV Reader`given a CSV data

####  Sample CSV Data (`my_dataset.csv`)

   Suppose we have a dataset concerning sales data for different products:

```Plain
ProductID,ProductName,Sales,ExpectedOutput
1001,WidgetA,500,High
1002,WidgetB,150,Low
1003,WidgetC,300,Medium
1004,WidgetD,,Low
1005,WidgetE,450,
```

   In this CSV:

- `ProductID` is a unique identifier for products.
- `ProductName` is the name of the product.
- `Sales` represent the number of units sold.
- `ExpectedOutput` is a categorical value indicating the sales volume (High, Medium, Low).

####  Using the CSVReader 

   Given the configuration below:

```Python
config = CSVReaderConfig(use_first_column_as_id=True, expected_result_column="ExpectedOutput")
csv_reader = CSVReader(config)
csv_file_path = "./data/my_dataset.csv"
```

   When we use the `read` method:

```Python
for chunk in csv_reader.read(csv_file_path):
    for data in chunk:
        print(data.content)
```

   The output would look like:

```Plain
{'ProductID': '1001', 'ProductName': 'WidgetA', 'Sales': '500'}
{'ProductID': '1002', 'ProductName': 'WidgetB', 'Sales': '150'}
{'ProductID': '1003', 'ProductName': 'WidgetC', 'Sales': '300'}
```



   **Note:**

- The row with `ProductID` 1004 is skipped because it has missing data in the `Sales` column.
- The row with `ProductID` 1005 is skipped because it lacks an `ExpectedOutput`.
- The `ExpectedOutput` column is not present in the content as it's marked for extraction.

####  Results & Handling

   The data extracted by the CSVReader will be in the form of `InputData` objects. Each object will have:

- `example_id`: The unique identifier (from the `ProductID` column, as specified by the `use_first_column_as_id` flag).
- `content`: The actual content of the row (excluding the `ExpectedOutput` column).
- `expected_result`: The extracted expected result from the `ExpectedOutput` column.



   For the row with `ProductID` 1001, the `InputData` object will look like:

```Plain
InputData(
    example_id='1001',
    content={'ProductID': '1001', 'ProductName': 'WidgetA', 'Sales': '500'},
    expected_result='High'
)
```

####  Using the CSVReader in YiVal config

```YAML
      dataset:
        file_path: demo/data/yival_expected_results.csv
        reader: csv_reader
        source_type: dataset
        reader_config:
          expected_result_column: expected_result
```

## `HuggingFaceDatasetReader`

###   Introduction 

  The `HuggingFaceDatasetReader` class provides an interface to read datasets directly from the HuggingFace Datasets server. It allows for fetching data, transforming its structure, and filtering based on inclusion and exclusion patterns.

###  Class Definition

####   `HuggingFaceDatasetReader(BaseReader)`

#####     Description

​    The `HuggingFaceDatasetReader` class, derived from `BaseReader`, is designed to read datasets from HuggingFace's Datasets server.

#####   Attributes 

- **`config (HuggingFaceDatasetReaderConfig)`**: Configuration object specifying the reader's parameters.

- **`default_config (HuggingFaceDatasetReaderConfig)`**: Default configuration for the reader.

#####  Methods 

- **`__init__(self, config: HuggingFaceDatasetReaderConfig)`**:
  - Initializes the `HuggingFaceDatasetReader` with the provided configuration.
  - Parameters:
    - `config (HuggingFaceDatasetReaderConfig)`: The configuration object for the reader.
- **`read(self, path: str) -> Iterator[List[InputData]]`**:
  - Reads the dataset from the specified HuggingFace Datasets server's URL and yields lists of `InputData`.
  - Parameters:
    - `path (str)`: URL pointing to the HuggingFace Datasets server.
  - Returns:
    - An iterator that produces lists of `InputData`.

####  `HuggingFaceDatasetReaderConfig(BaseReaderConfig)`

#####  Description

​    The configuration object is specific to the `HuggingFaceDatasetReader` class.

#####  Attributes

- **`example_limit (int)`**:
  - The maximum number of examples to fetch from the dataset. 
  - The default value is `1`.
- **`output_mapping (Dict[str, str])`**:
  - A mapping to transform the keys in the dataset. The `Dict` key is the original dataset key, and the corresponding value is the new key. 
  - The default value is an empty dictionary or `{}`.

- **`include (List[str])`**:
  - List of regex patterns. Only items matching these patterns will be included.
  - The default value is an empty list or`[]`.
- **`exclude (List[str])`**:
  -  List of regex patterns. Items matching these patterns will be excluded.
  - The default value is an empty list or `[]`.

###  Example 

####  Filtering Out Hard Leetcode Problems in HugginFace Dataset

   In the example below, the reader fetches data from the given HuggingFace Datasets server's URL, transforms the key "question" to "leetcode_problem", and filters out any entry labeled as "Hard".

```Python
# Assuming necessary imports are in place

# Define the reader configuration
config = HuggingFaceDatasetReaderConfig(
    chunk_size=1000,
    example_limit=100,
    output_mapping={'question': 'leetcode_problem'},
    include=['^(?!.*# Hard).*$']
)

# Create an instance of HuggingFaceDatasetReader with the specified configuration
reader = HuggingFaceDatasetReader(config)

# Define the URL pointing to the HuggingFace Datasets server
url = "https://datasets-server.huggingface.co/rows?dataset=BoyuanJackchen%2Fleetcode_free_questions_text&config=default&split=train"

# Read and process data
for data_chunk in reader.read(url):
    for data in data_chunk:
        print(data.content)
```

####  Using the HuggingFaceDatasetReader in YiVal config: 

```YAML
  dataset:
    file_path: https://datasets-server.huggingface.co/rows?dataset=griffin%2Fchain_of_density&config=annotated&split=test
    reader: huggingface_dataset_reader
    source_type: dataset
    reader_config:
      example_limit: 2
      output_mapping:
        article: article
```

###  [Source Code](https://github.com/YiVal/YiVal/blob/master/src/yival/data/huggingface_dataset_reader.py)

## Custom Reader Guide: `TXTReader`

 This guide provides the steps to create custom data readers by subclassing the provided `BaseReader` class. The example demonstrates creating a `TXTReader` to read `.txt` files.

###  Introduction

  Data readers are responsible for reading data from various sources. By subclassing the `BaseReader`, you can create custom readers tailored to your specific data format needs.

###  `BaseReader` Overview

  The `BaseReader` class offers a blueprint for designing data readers. It has methods for:

- Register new readers.
- Retrieve registered readers and their configurations.
- Read data in chunks.

  The class provides an abstract method `read` that you must override in your custom reader. The method is designed to read data in chunks for efficient parallel processing.

###  Creating a Custom Reader (`TXTReader`)

####  Design the TXTReaderConfig Class

   Before creating the reader, design a configuration class specific to the `TXTReader`. This class will inherit from the base `BaseReaderConfig`:

```Python
from dataclasses import asdict, dataclass
from yival.data.base_reader import BaseReaderConfig

@dataclass
class TXTReaderConfig(BaseReaderConfig):    
    """    
    Configuration specific to the TXT reader.    
    """
    delimiter: str = "\n"  # Default delimiter for txt files.
    
    def asdict(self):
        return asdict(self)
```

####  Implement the TXTReader Class

   Now, create the `TXTReader` class, subclassing the `BaseReader`:

```Python
from typing import Iterator, List

from txt_reader_config import TXTReaderConfig
from yival.data.base_reader import BaseReader
from yival.schemas.common_structures import InputData

class TXTReader(BaseReader):
    """
    TXTReader is a class derived from BaseReader to read datasets from TXT
    files.

    Attributes:
        config (TXTReaderConfig): Configuration object specifying reader parameters.

    Methods:
        __init__(self, config: TXTReaderConfig): Initializes the TXTReader with
        a given configuration.
        read(self, path: str) -> Iterator[List[InputData]]: Reads the TXT file
        and yields chunks of InputData.
    """

    config: TXTReaderConfig
    default_config = TXTReaderConfig()

    def __init__(self, config: TXTReaderConfig):
        super().__init__(config)
        self.config = config

    def read(self, path: str) -> Iterator[List[InputData]]:
        chunk = []
        chunk_size = self.config.chunk_size

        with open(path, mode="r", encoding="utf-8") as file:
            for line in file:
                line_content = line.strip().split(self.config.delimiter)

                # Each line in the TXT file is treated as a separate data point.
                example_id = self.generate_example_id({"content": line_content}, path)
                input_data_instance = InputData(
                    example_id=example_id,
                    content=line_content
                )
                chunk.append(input_data_instance)

                if len(chunk) >= chunk_size:
                    yield chunk
                    chunk = []

            if chunk:
                yield chunk
```

####  Config

   After defining the config and reader subclass, we can define the yml config file:

```YAML
custom_reader:  
    txt_reader:    
        class: /path/to/text_reader.TXTReader    
        config_cls: /path/to/txt_reader_config.TXTReaderConfig
```



```YAML
dataset:  
    source_type: dataset  
    reader: txt_reader  
    file_path: "/Users/taofeng/YiVal/data/headline_generation.txt"  
    reader_config:   
    delimiter: "\n"
```

###  Conclusion

  Creating custom data readers with the provided framework is straightforward. You can design readers tailored to various data formats by simply subclassing the `BaseReader` and overriding its `read` method. With this capability, you can efficiently read data in chunks, making it suitable for parallel processing and large datasets.