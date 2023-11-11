---
sidebar_position: 9
---

# Data Generation  

##  `BaseDataGenerator`

###   Introduction 

  This class provides a blueprint for data generators and offers methods to register new generators, retrieve registered generators, and fetch their configurations.



###   Class Definition 

####    Description

####    Attributes



###   Example

##  `OpenAIPromptDataGenerator`

###   Introduction 

  This module provides a mechanism for data generation using OpenAI's models. It aims to generate data examples programmatically based on a given prompt and configuration. The generated examples can be used for various purposes including testing, simulations, and more. The module offers utility functions to process and transform the generated data, ensuring it's structured and usable for subsequent operations.

###   Class Definition 

####    Description

   This configuration object is specifically tailored for the `OpenAIPromptDataGenerator` class. It provides settings to guide the generation of test cases using OpenAI models based on a given prompt.

####    Attributes

- **`model_name(str)`**:
  -  Specifies the OpenAI model to be used for generating the test cases. 
  - The default value is `"gpt-4"`.
- **`prompt (Union[str, List[Dict[str, str]]])`**: 
  - The instruction or set of instructions given to the OpenAI model for generating test cases. It can be a single string or a list of messages. 
  - The default value is  an empty string or `""`.
- **`input_function (Dict[str, Any])`**:
  -  Details of the function for which test cases are to be generated. Contains information like function name, description, and parameters. 
  - The default value is an empty dictionary or `{}`.
- **`diversify(bool)`**: 
  - A flag that determines if the generated test cases should be diversified to ensure comprehensive evaluation. 
  - The default value is set to `True`.
- **`max_token(int)`**: 
  - Specifies the maximum number of tokens allowed for the prompt. 
  - The default value is set to `2000`.
- **`expected_param_name(str)`**: 
  - Indicates the name of the parameter that contains expected values in the generated test cases.
- **`call_option(Optional[CallOption])`**: 
  - Provides additional options for calling the OpenAI model. 
  - The default value is `None`.
- **`output_csv_path(Optional[str])`**: 
  - The path to save the generated test cases in a CSV format. 
  - The default value is `None`.

###   Example

####    Generate Data and Save Test Case

```Python
# Create a configuration for data generation
generator_config = OpenAIPromptBasedGeneratorConfig(
    prompt="Please provide test cases for...",
    input_function={
        "name": "example_function",
        "description": "Describe the function...",
        "parameters": {
            "param1": "str",
            "param2": "int"
        }
    },
    diversify=True,
    max_token=1500,
    expected_param_name="expected_output",
    output_csv_path="path/to/save/test_cases.csv"
)

# Initialize the data generator with the configuration
data_generator = OpenAIPromptDataGenerator(generator_config)

# Generate and save test cases
data_generator.generate_examples()
```

####    Use OpenAI Prompt Data Generator in the YiVal config

```YAML
dataset:
  data_generators:
    openai_prompt_data_generator:
      chunk_size: 2
      diversify: true
      prompt:
          "Please provide a concrete and realistic test case as a dictionary for function invocation using the ** operator.
          Only include parameters, excluding description and name.
          Ensure it's succinct and well-structured.
          **Only provide the dictionary.**"
      input_function:
        description:
          Given the species of an animal and its character, generate a corresponding story
        name: animal_story_generation
        parameters:
          species: str
          character: str
          drawing_style: str
      number_of_examples: 2
      model_name: gpt-4
      output_path: animal_story.pkl
  source_type: machine_generated
```



###   [Source Code](https://github.com/YiVal/YiVal/blob/master/src/yival/data_generators/openai_prompt_data_generator.py)



##  Custom Data Generator Guide: `ListStringDataGenerator`

  This guide will walk you through creating a custom data generator using the provided `BaseDataGenerator`.

###   Introduction

  The ability to programmatically generate data is crucial in scenarios where synthetic or mock data is required, such as in testing, simulations, and more. The provided foundational architecture for data generators allows flexibility and extensibility, enabling you to create custom data generators tailored to specific needs.

  In this guide, we will demonstrate how to create a custom data generator by extending the BaseDataGenerator. Our custom generator will output a list of predefined strings. By following this guide, you'll gain an understanding of the structure and process, enabling you to develop even more complex generators as needed.

###   Subclassing the `BaseDataGenerator`

  First, create a `ListStringDataGenerator` that simply outputs a list of strings as specified in its configuration.

```Python
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

------

###   Providing a Configuration Class

  To specify the list of strings our generator should output, define a custom configuration class:

```Python
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

###   Config

  In your configuration (YAML), you can now specify the use of this data generator:

```YAML
custom_data_generators:
  list_string_data_generator:
    class: /path/to/list_string_data_generator.ListStringDataGenerator
    config_cls: /path/to/list_string_data_generator_config.ListStringGeneratorConfig
```

```YAML
dataset:
  data_generators:
    list_string_data_generator:
      strings_to_generate:
        - abc
        - def
  source_type: machine_generated
```
