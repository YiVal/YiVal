# Custom Combination Enhancer Creation Guide

## Introduction

Combination enhancers play a pivotal role in the experimental framework by
optimizing the combination of experiments based on their outcomes. By leveraging
combination enhancers, experiments can be fine-tuned to achieve better results.
This guide will outline the process of creating a custom combination enhancer.

## Table of Contents

1. Introduction
2. Overview of Base Combination Enhancer
3. Implementing a Custom Combination Enhancer
4. Registering the Custom Combination Enhancer
5. Conclusion

## Overview of Base Combination Enhancer

The `BaseCombinationEnhancer` class provides the foundational structure for all
combination enhancers. It offers methods to:

- Register new combination enhancers.
- Fetch registered combination enhancers.
- Retrieve their default configurations.

The main responsibility of a combination enhancer is to enhance the setup of
experiments based on their results.

## Implementing a Custom Combination Enhancer

To create a custom combination enhancer, one should inherit from the `BaseCombinationEnhancer`
class and implement the `enhance` abstract method:

```python

class CustomCombinationEnhancer(BaseCombinationEnhancer):
    """
    Custom combination enhancer to optimize the setup of experiments.
    """

    def enhance(self, experiment, config, evaluator, token_logger):
        """
        Custom logic to enhance the experiment based on its results.

        Args:
            experiment (Experiment): The experiment with its results.
            config (ExperimentConfig): The original experiment configuration.
            evaluator (Evaluator): A utility class to evaluate the
            ExperimentResult.
            token_logger (TokenLogger): Logs the token usage.

        Returns:
            EnhancerOutput: The result of the enhancement.
        """

        # Custom logic for enhancement goes here
        pass
```

## Config

```yaml
custom_enhancers:
    class: /path/to/custom_enhancer.CustomEnhancer
    config_cls: /path/to/custom_enhancer_config.CustomEnhancerConfig
```

To use it

```yaml
enhancer:
  name: custom_enhancer
```

## Conclusion

By following this guide, you have successfully created and registered a custom
combination enhancer named `CustomCombinationEnhancer` within the experimental
framework. This custom enhancer will allow you to optimize experiment combinations
based on specific logic and criteria you define. As experiments evolve and grow in
complexity, custom combination enhancers like the one you've developed will become
instrumental in achieving more refined and better results.
