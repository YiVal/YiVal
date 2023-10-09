<a id="yival.data_generators.base_data_generator"></a>

# yival.data\_generators.base\_data\_generator

This module provides a foundational architecture for programmatically
generating data.

Data generators are responsible for creating data programmatically based on
certain configurations.
The primary utility of these generators is in scenarios where synthetic or
mock data is required,
such as testing, simulations, and more. This module offers a base class that
outlines the primary
structure and functionalities of a data generator. It also provides methods to
register new
generators, retrieve existing ones, and fetch their configurations.

<a id="yival.data_generators.base_data_generator.BaseDataGenerator"></a>

## BaseDataGenerator Objects

```python
class BaseDataGenerator(ABC)
```

Abstract base class for all data generators.

This class provides a blueprint for data generators and offers methods to
register new generators,
retrieve registered generators, and fetch their configurations.

**Attributes**:

- `_registry` _Dict[str, Dict[str, Any]]_ - A registry to keep track of
  data generators.
- `default_config` _Optional[BaseDataGeneratorConfig]_ - Default
  configuration for the generator.

<a id="yival.data_generators.base_data_generator.BaseDataGenerator.get_data_generator"></a>

#### get\_data\_generator

```python
@classmethod
def get_data_generator(cls, name: str) -> Optional[Type['BaseDataGenerator']]
```

Retrieve data generator class from registry by its name.

<a id="yival.data_generators.base_data_generator.BaseDataGenerator.get_default_config"></a>

#### get\_default\_config

```python
@classmethod
def get_default_config(cls, name: str) -> Optional[BaseDataGeneratorConfig]
```

Retrieve the default configuration of a data generator by its
name.

<a id="yival.data_generators.base_data_generator.BaseDataGenerator.get_config_class"></a>

#### get\_config\_class

```python
@classmethod
def get_config_class(cls,
                     name: str) -> Optional[Type[BaseDataGeneratorConfig]]
```

Retrieve the configuration class of a generator_info by its name.

<a id="yival.data_generators.base_data_generator.BaseDataGenerator.register_data_generator"></a>

#### register\_data\_generator

```python
@classmethod
def register_data_generator(
        cls,
        name: str,
        data_generator_cls: Type['BaseDataGenerator'],
        config_cls: Optional[Type[BaseDataGeneratorConfig]] = None)
```

Register data generator class with the registry.

<a id="yival.data_generators.base_data_generator.BaseDataGenerator.generate_examples"></a>

#### generate\_examples

```python
@abstractmethod
def generate_examples() -> Iterator[List[InputData]]
```

Generate data examples and return an iterator of lists containing
InputData.

This method is designed to produce data programmatically. The number
and nature of data examples are determined by the generator's
configuration.

**Returns**:

- `Iterator[List[InputData]]` - An iterator yielding lists of InputData
  objects.

<a id="yival.data_generators.base_data_generator.BaseDataGenerator.generate_example_id"></a>

#### generate\_example\_id

```python
def generate_example_id(content: str) -> str
```

Generate a unique identifier for a given content string.

**Arguments**:

- `content` _str_ - The content for which an ID should be generated.
  

**Returns**:

- `str` - A unique MD5 hash derived from the content.

<a id="yival.data_generators.openai_prompt_data_generator"></a>

# yival.data\_generators.openai\_prompt\_data\_generator

This module provides an implementation for data generation using OpenAI's
model.

The primary goal of this module is to programmatically generate data examples
based on a given prompt and configuration. It employs OpenAI's models to
produce
these examples, and offers utility functions for transforming and processing
the generated data.

<a id="yival.data_generators.openai_prompt_data_generator.OpenAIPromptDataGenerator"></a>

## OpenAIPromptDataGenerator Objects

```python
class OpenAIPromptDataGenerator(BaseDataGenerator)
```

Data generator using OpenAI's model based on provided prompts and
configurations.

This class is responsible for the generation of data examples using
OpenAI's models.
The generated data can be used for various purposes, including testing,
simulations, and more. The nature and number of generated examples are
determined by the provided configuration.

<a id="yival.data_generators.openai_prompt_data_generator.OpenAIPromptDataGenerator.prepare_messages"></a>

#### prepare\_messages

```python
def prepare_messages(all_data_content) -> List[Dict[str, Any]]
```

Prepare the messages for GPT API based on configurations.

<a id="yival.data_generators.openai_prompt_data_generator.OpenAIPromptDataGenerator.process_output"></a>

#### process\_output

```python
def process_output(output_content: str, all_data: List[InputData],
                   chunk: List[InputData])
```

Process the output from GPT API and update data lists.

