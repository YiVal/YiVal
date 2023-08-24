# Writing a Custom Variation Generator Subclass

This guide explains how to create a custom variation generator subclass based on
the `BaseVariationGenerator` for experimental variations.

## 1. Understand the Base

The `BaseVariationGenerator` provides foundational methods and attributes for all
variation generators. Subclasses should implement the `generate_variations`
method to define the logic for producing variations.

## 2. Example: SimpleVariationGenerator

Let's design a generator that simply returns variations based on the configurations
provided.

#### 2.1 Define the Configuration Class

Firstly, you'll need a configuration class specific to your generator:

```python
from dataclasses import dataclass
from yival.schemas.varation_generator_configs import BaseVariationGeneratorConfig

@dataclass
class SimpleVariationGeneratorConfig(BaseVariationGeneratorConfig):
    variations: Optional[List[str]] = None  # List of variations to generate
```

This configuration class inherits from `BaseVariationGeneratorConfig` and has an
additional attribute, `variations`, which is a list of variation strings.

#### 2.2 Implement the Variation Generator

Now, let's create the custom variation generator:

```python
from typing import Iterator, List

from yival.schemas.experiment_config import WrapperVariation
from yival.variation_generators.base_variation_generator import BaseVariationGenerator

class SimpleVariationGenerator(BaseVariationGenerator):
    
    def __init__(self, config: SimpleVariationGeneratorConfig):
        super().__init__(config)
        self.config = config
    
    def generate_variations(self) -> Iterator[List[WrapperVariation]]:
        variations = [WrapperVariation(value_type="str", value=var) for var in self.config.variations]
        yield variations
```

Here, the `generate_variations` method simply converts the list of variation
strings from the configuration into a list of `WrapperVariation` objects and yields
it.

### 3. Using the Custom Variation Generator in Configuration

In your configuration (YAML), you can now specify the use of this variation
generator:

```yml
custom_variation_generators:
  simple_variation_generator:
    class: /path/to/simple_variation_generator.SimpleVariationGenerator
    config_cls: /path/to/simple_variation_generator_config.SimpleVariationGeneratorConfig
```

```yaml
variations:
  - name: task
    generator_name: simple_variation_generator
    generator_config:
      variations:
        - abc
        - def
```

This configuration will use the `SimpleVariationGenerator` and produce the
variations "variation1" and "variation2".
