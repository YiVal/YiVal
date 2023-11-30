---
sidebar_position: 12

---

# Variation Generator

## `BaseVariationImprover`

### Introduction

  This module defines the base class for combination improvers. Combination improvers are responsible for improving the combination of experiments based on their experiment results.

### Class Definition

#### Description

#### Attributes

### Example

## `OpenAIPromptBasedVariationGenerator`

### Introduction

  A variation generator that uses the GPT-4 model to generate variations based on the provided prompt configurations.

### Class Definition

#### Description

   A data class defining the configuration for the `OpenAIPromptBasedVariationGenerator`.

#### Attributes

- **`model_name(str)`**:
    - The name of the model to be used. The default value is `"gpt-4"`.
- **`prompt(Union[str, List[Dict[str, str]]])`**:
    - The prompt or set of prompts that guide the generation of variations.
- **`diversify(bool)`**:
    - Whether to ensure diversification in the generated responses.
- **`variables(Optional[List[str]])`**:
    - Specific variables that should be included in the generated variations.
- **`max_tokens(int)`**:
    - The maximum number of tokens for the generated response. The default value is `7000`.

### Example

#### Using `OpenAIPromptBasedVariationGenerator`

```Python
    generator = OpenAIPromptBasedVariationGenerator(
        OpenAIPromptBasedVariationGeneratorConfig(
            prompt=[{
                "role": "system",
                "content": SYSTEM_PRMPOT
            }, {
                "role":
                "user",
                "content":
                "Here are some test cases: AI, Weapon\n\n Here is the description of the use-case: Given \{area\}, write a tech startup headline"
            }],
            number_of_variations=2,
            output_path="test_variation.pkl",
            diversify=False,
            variables=["area"]
        )
    )
    res = generator.generate_variations()
    for d in res:
        print(d)
```

#### Using the `OpenAIPromptBasedCombinationImprover` in YiVal config

```Python
variations:
  - name: task
    generator_name: openai_prompt_based_variation_generator
    generator_config:
      diversify: false
      max_tokens: 7000
      number_of_variations: 2
      model_name: gpt-4
      output_path: demo_generated_prompt.pkl
      prompt:
        - content: |-

            Your mission is to craft prompts tailored for GPT-4. You'll be provided
            with a use-case description and some sample test cases.

            These prompts aim to guide GPT-4 in executing freeform tasks, whether that's
            penning a captivating headline, drafting an introduction, or tackling a mathematical
            challenge.

            In your designed prompt, delineate the AI's role using lucid English. Highlight
            its perceptual field and the boundaries of its responses. Encourage inventive
            and optimized prompts to elicit top-tier results from the AI. Remember, GPT-4
            is self-aware of its AI nature; no need to reiterate that.

            The efficacy of your prompt determines your evaluation. Stay authentic! Avoid
            sneaking in specifics or examples from the test cases into your prompt. Such
            maneuvers will lead to immediate disqualification.

            Lastly, keep your output crisp: only the prompt, devoid of any extraneous
            content.

          role: system
        - content: |-
            Use case description: Given an tech startup business, generate a corresponding landing page headline
            Test Cases: Food Delivery, AI Developer tools.
          role: user
        - content: |-
            {tech_startup_business} represent the specific test cases.
          role: user
      variables:
        - tech_startup_business
```

## Custom Variation Generator Subclass Guide: `generate_variations`

 This guide explains how to create a custom variation generator subclass based on the `BaseVariationGenerator` for experimental variations.

### Understand the Base

  The `BaseVariationGenerator` provides foundational methods and attributes for all variation generators. Subclasses should implement the `generate_variations` method to define the logic for producing variations.

#### Example: SimpleVariationGenerator

  Let's design a generator that simply returns variations based on the configurations provided.

### Define the Configuration Class

  Firstly, you'll need a configuration class specific to your generator:

```Python
from dataclasses import dataclass
from yival.schemas.varation_generator_configs import BaseVariationGeneratorConfig

@dataclass
class SimpleVariationGeneratorConfig(BaseVariationGeneratorConfig):
    variations: Optional[List[str]] = None  # List of variations to generate
```

  This configuration class inherits from `BaseVariationGeneratorConfig` and has an additional attribute, `variations`, which is a list of variation strings.

### Implement the Variation Generator

  Now, let's create the custom variation generator:

```Python
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

  Here, the `generate_variations` method simply converts the list of variation strings from the configuration into a list of `WrapperVariation` objects and yields it.

#### Using the Custom Variation Generator in Configuration

  In your configuration (YAML), you can now specify the use of this variation generator:

```YAML
custom_variation_generators:
  simple_variation_generator:
    class: /path/to/simple_variation_generator.SimpleVariationGenerator
    config_cls: /path/to/simple_variation_generator_config.SimpleVariationGeneratorConfig
```

```Plaintext
variations:
  - name: task
    generator_name: simple_variation_generator
    generator_config:
      variations:
        - abc
        - def
```

  This configuration will use the `SimpleVariationGenerator` and produce the variations "variation1" and "variation2".
