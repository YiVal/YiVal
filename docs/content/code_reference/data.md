<a id="yival.data.huggingface_dataset_reader"></a>

# yival.data.huggingface\_dataset\_reader

<a id="yival.data.csv_reader"></a>

# yival.data.csv\_reader

Read data from CSV

<a id="yival.data.csv_reader.get_valid_path"></a>

#### get\_valid\_path

```python
def get_valid_path(user_specified_path)
```

Get valid csv input path.

<a id="yival.data.csv_reader.CSVReader"></a>

## CSVReader Objects

```python
class CSVReader(BaseReader)
```

CSVReader is a class derived from BaseReader to read datasets from CSV
files.

**Attributes**:

- `config` _CSVReaderConfig_ - Configuration object specifying reader
  parameters.
- `default_config` _CSVReaderConfig_ - Default configuration for the
  reader.
  

**Methods**:

  __init__(self, config: CSVReaderConfig): Initializes the CSVReader
  with a given configuration.
  read(self, path: str) -> Iterator[List[InputData]]: Reads the CSV
  file and yields chunks of InputData.
  

**Notes**:

  The read method checks for headers in the CSV file and raises an
  error if missing.
  It also checks for missing data in rows, skipping those with
  missing values but logs them.
  If a specified column contains expected results, it extracts those
  results from the row.
  Rows are read in chunks, and each chunk is yielded once its size
  reaches `chunk_size`.
  The class supports registering with the BaseReader using the
  `register_reader` method.
  
  Usage:
  reader = CSVReader(config)
  for chunk in reader.read(path_to_csv_file):
  process(chunk)

<a id="yival.data.base_reader"></a>

# yival.data.base\_reader

This module provides an abstract foundation for data readers.

Data readers are responsible for reading data from various sources, and this
module offers a base class to define and register new readers, retrieve
existing ones, and fetch their configurations. The design encourages efficient
parallel processing by reading data in chunks.

<a id="yival.data.base_reader.BaseReader"></a>

## BaseReader Objects

```python
class BaseReader(ABC)
```

Abstract base class for all data readers.

This class provides a blueprint for data readers and offers methods to
register new readers,
retrieve registered readers, and fetch their configurations.

**Attributes**:

- `_registry` _Dict[str, Dict[str, Any]]_ - A registry to keep track of
  data readers.
- `default_config` _Optional[BaseReaderConfig]_ - Default configuration for
  the reader.

<a id="yival.data.base_reader.BaseReader.register"></a>

#### register

```python
@classmethod
def register(cls,
             name: str,
             config_cls: Optional[Type[BaseReaderConfig]] = None)
```

Decorator to register new readers.

<a id="yival.data.base_reader.BaseReader.get_reader"></a>

#### get\_reader

```python
@classmethod
def get_reader(cls, name: str) -> Optional[Type['BaseReader']]
```

Retrieve reader class from registry by its name.

<a id="yival.data.base_reader.BaseReader.get_default_config"></a>

#### get\_default\_config

```python
@classmethod
def get_default_config(cls, name: str) -> Optional[BaseReaderConfig]
```

Retrieve the default configuration of a reader by its name.

<a id="yival.data.base_reader.BaseReader.get_config_class"></a>

#### get\_config\_class

```python
@classmethod
def get_config_class(cls, name: str) -> Optional[Type[BaseReaderConfig]]
```

Retrieve the configuration class of a reader by its name.

<a id="yival.data.base_reader.BaseReader.register_reader"></a>

#### register\_reader

```python
@classmethod
def register_reader(cls,
                    name: str,
                    reader_cls: Type['BaseReader'],
                    config_cls: Optional[Type[BaseReaderConfig]] = None)
```

Register reader's subclass along with its default configuration and
config class.

<a id="yival.data.base_reader.BaseReader.read"></a>

#### read

```python
@abstractmethod
def read(path: str) -> Iterator[List[InputData]]
```

Read data from the given file path and return an iterator of lists
containing InputData.

This method is designed to read data in chunks for efficient parallel
processing. The chunk size is determined by the reader's configuration.

**Arguments**:

- `path` _str_ - The path to the file containing data to be read.
  

**Returns**:

- `Iterator[List[InputData]]` - An iterator yielding lists of InputData
  objects.

<a id="yival.data.base_reader.BaseReader.generate_example_id"></a>

#### generate\_example\_id

```python
def generate_example_id(row_data: Dict[str, Any], path: str) -> str
```

Default function to generate an example_id for a given row of data.

