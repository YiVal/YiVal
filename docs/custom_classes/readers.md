# Writing a Custom Data Reader in Python with BaseReader

This guide provides steps on how to create custom data readers by subclassing the
provided `BaseReader` class. The example demonstrates how to create a `TXTReader`
to read `.txt` files.

## Table of Contents

1. Introduction
2. BaseReader Overview
3. Creating a Custom Reader (TXTReader)
4. Conclusion

## 1. Introduction

Data readers are responsible for reading data from various sources. By subclassing
the `BaseReader`, you can create custom readers tailored to your specific data
format needs.

## 2. BaseReader Overview

The `BaseReader` class offers a blueprint for designing data readers. It has
methods to:

- Register new readers.
- Retrieve registered readers and their configurations.
- Read data in chunks.

The class provides an abstract method `read` that you must override in your
custom reader. The method is designed to read data in chunks for efficient
parallel processing.

## 3. Creating a Custom Reader (TXTReader)

### 3.1. Design the TXTReaderConfig Class

Before creating the reader, design a configuration class specific to the `TXTReader`.
This class will inherit from the base `BaseReaderConfig`:

```python
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

### 3.2. Implement the TXTReader Class

Now, create the `TXTReader` class, subclassing the `BaseReader`:

```python

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

### 3.3. Config

After defining the config and reader sublass, we can define the yml config:

```yml
custom_reader:
  txt_reader:
    class: /path/to/text_reader.TXTReader
    config_cls: /path/to/txt_reader_config.TXTReaderConfig
```

```yaml
dataset:
  source_type: dataset
  reader: txt_reader
  file_path: "/Users/taofeng/YiVal/data/headline_generation.txt"
  reader_config:
    delimiter: "\n"
```

## 4. Conclusion

Creating custom data readers with the provided framework is straightforward. You
can design readers tailored to various data formats by simply subclassing the
`BaseReader` and overriding its `read` method. With this capability, you can
efficiently read data in chunks, making it suitable for parallel processing and
large datasets.
