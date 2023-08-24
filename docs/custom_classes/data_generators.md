# Creating a Custom Data Generator with `BaseDataGenerator`

This guide will walk you through creating a custom data generator using the
provided `BaseDataGenerator`.

## Introduction

The ability to programmatically generate data is crucial in scenarios where
synthetic or mock data is required, such as in testing, simulations, and more.
The provided foundational architecture for data generators allows for
flexibility and extensibility, enabling you to create custom data generators
tailored to specific needs.

In this guide, we will demonstrate how to create a custom data generator by
extending the BaseDataGenerator. Our custom generator will output a list of
predefined strings. By following this guide, you'll gain an understanding of
the structure and process, enabling you to develop even more complex generators
as needed.

## Step 1: Subclassing the `BaseDataGenerator`

First, create a `ListStringDataGenerator` that simply outputs a list of strings
as specified in its configuration.

```python
from typing import Iterator, List

from list_string_data_generator_config import ListStringGeneratorConfig
from yival.data_generators.base_data_generator import BaseDataGenerator
from yival.schemas.common_structures import InputData



class ListStringDataGenerator(BaseDataGenerator):
    def __init__(self, config: 'ListStringGeneratorConfig'):
        super().__init__(config)

    def generate_examples(self) -> Iterator[List[InputData]]:
        for string_data in self.config.strings_to_generate:
            yield [InputData(example_id=self.generate_example_id(string_data), content=string_data)]
```

---

### Step 2: Providing a Configuration Class

To specify the list of strings our generator should output, define a custom
configuration class:

```python
from dataclasses import dataclass, field
from typing import List

from yival.schemas.data_generator_configs import BaseDataGeneratorConfig


@dataclass
class ListStringGeneratorConfig(BaseDataGeneratorConfig):
    """
    Configuration for the ListStringDataGenerator.
    """
    strings_to_generate: List[str] = field(default_factory=list)
```

### Config

In your configuration (YAML), you can now specify the use of this data
generator:

```yml
custom_data_generators:
  list_string_data_generator:
    class: /path/to/list_string_data_generator.ListStringDataGenerator
    config_cls: /path/to/list_string_data_generator_config.ListStringGeneratorConfig
```

```yaml
dataset:
  data_generators:
    list_string_data_generator:
      strings_to_generate:
        - abc
        - def
  source_type: machine_generated
```
