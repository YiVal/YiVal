---
sidebar_position: 5
---

# Wrapper

## `BaseWrapper`

### Introduction

  This module introduces the `BaseWrapper` class, which serves as the fundamental structure for wrappers in the experimental framework. Wrappers manage experiment variations based on the global experiment state. They are crucial components to control and monitor different variations during an experiment's lifecycle.

### Class Definition

#### Description

   Base class for wrappers that manage experiment variations based on the global experiment state. This class provides the fundamental structure and methods for wrappers. Specific wrappers should inherit from this class and implement the necessary methods.

#### Attributes

- **`name(str)`**:
    - The name of the wrapper.
- **`experiment_state(ExperimentState)`**:
    - The global state of the experiment.
- **`config(BaseWrapperConfig)`**:
    - The configuration for the wrapper.

### Example

### [Source Code](https://github.com/YiVal/YiVal/blob/master/src/yival/wrappers/base_wrapper.py)

## `StringWrapper`

### Introduction

  This module provides a `StringWrapper` class designed to manage string variations based on the current experiment state. It helps in retrieving and formatting string variations in the context of an active experiment.

### Class Definition

#### Description

#### Attributes

### Example

```Python
wrapper = StringWrapper(template="Hello, {name}!", name="greeting_experiment", variables={"name": "John"})
print(str(wrapper))  # This will print the appropriate greeting based on the experiment state.
```

### [Source Code](https://github.com/YiVal/YiVal/blob/master/src/yival/wrappers/string_wrapper.py)

## Custom Wrapper Guide: `NumberWrapper`

### Introduction

  In the experimental framework, wrappers play a vital role in managing variations throughout an experiment's lifecycle. By creating custom wrappers, one can control and monitor variations tailored to specific needs, ensuring that the experiment operates smoothly and efficiently.

  In this guide, we will walk you through the process of creating a custom wrapper named `NumberWrapper`. This wrapper will handle variations specifically for numbers. By the end of this guide, you will have a clear understanding of creating and registering a custom wrapper within the experimental framework.

### Base Wrapper Overview

  The `BaseWrapper` class provides the fundamental structure for wrappers. It comes equipped with methods to register new wrappers, retrieve registered ones, and fetch their configurations. The primary purpose of a wrapper is to manage experiment variations based on the global experiment state.

### Creating a `NumberWrapper`

  The `NumberWrapper` will be a custom wrapper designed to handle variations specifically for numbers.

```Python
from typing import Optional

from number_wrapper_config import NumberWrapperConfig
from yival.wrappers.base_wrapper import BaseWrapper

class NumberWrapper(BaseWrapper):
    """
    A wrapper for numbers to manage experiment variations based on the global
    experiment state. If a variation for the given experiment name exists and
    the global ExperimentState is active, the variation is used. Otherwise,
    the original number is returned.
    """
    default_config = NumberWrapperConfig()

    def __init__(
        self,
        value: float,
        name: str,
        config: Optional[NumberWrapperConfig] = None
        state: Optional[ExperimentState] = None
    ) -> None:
        super().__init__(name, config, state)
        self._value = value

    def get_value(self) -> float:
        variation = self.get_variation()
        if variation is not None:
            return variation
        return self._value
       
 
```

  Here, the `NumberWrapper` class is responsible for retrieving a variation if one exists, otherwise it returns the original number. The `get_value` method is used to fetch the number, considering any variations.

### Registering the `NumberWrapper`

  To make the `NumberWrapper` usable within the experimental framework, it needs to be registered. The registration process involves mapping the wrapper's name to its class and configuration.

```Python
from dataclasses import dataclass

from yival.schemas.wrapper_configs import BaseWrapperConfig

@dataclass
class NumberWrapperConfig(BaseWrapperConfig):
    """
    Configuration specific to the NumberWrapper.
    """
    pass
```

  By calling the `register_wrapper` method, the `NumberWrapper` becomes available for use in the experimental framework.

### Config

  Now you can configure the wrapper in the yml file:

```YAML
custom_wrappers:
  number_wrapper:
    class: /path/to/number_wrapper.NumberWrapper
    config_cls: /path/to/number_wrapper_config.NumberWrapperConfig
```

  And you should be able to use the wrapper in your code like a string wrapper.

### Conclusion

  By following this guide, you've successfully created and registered a custom wrapper named `NumberWrapper` in the experimental framework. This flexibility allows you to tailor experiments to specific needs, ensuring accurate and efficient results.
