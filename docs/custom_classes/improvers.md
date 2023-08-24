s# Custom Combination Improver Creation Guide

## Introduction

Combination improvers play a pivotal role in the experimental framework by
optimizing the combination of experiments based on their outcomes. By leveraging
combination improvers, experiments can be fine-tuned to achieve better results.
This guide will outline the process of creating a custom combination improver.

## Table of Contents

1. Introduction
2. Overview of Base Combination Improver
3. Implementing a Custom Combination Improver
4. Registering the Custom Combination Improver
5. Conclusion

## Overview of Base Combination Improver

The `BaseCombinationImprover` class provides the foundational structure for all
combination improvers. It offers methods to:

- Register new combination improvers.
- Fetch registered combination improvers.
- Retrieve their default configurations.

The main responsibility of a combination improver is to improve the setup of
experiments based on their results.

## Implementing a Custom Combination Improver

To create a custom combination improver, one should inherit from the `BaseCombinationImprover`
class and implement the `improve` abstract method:

```python

class CustomCombinationImprover(BaseCombinationImprover):
    """
    Custom combination improver to optimize the setup of experiments.
    """

    def improve(self, experiment, config, evaluator, token_logger):
        """
        Custom logic to improve the experiment based on its results.

        Args:
            experiment (Experiment): The experiment with its results.
            config (ExperimentConfig): The original experiment configuration.
            evaluator (Evaluator): A utility class to evaluate the
            ExperimentResult.
            token_logger (TokenLogger): Logs the token usage.

        Returns:
            ImproverOutput: The result of the improvement.
        """

        # Custom logic for improvement goes here
        pass
```

## Config

```yml
custom_improvers:
    class: /path/to/custom_improver.CustomImprover
    config_cls: /path/to/custom_improver_config.CustomImproverConfig
```

To use it

```yml
improver:
  name: custom_improver
```

## Conclusion

By following this guide, you have successfully created and registered a custom
combination improver named `CustomCombinationImprover` within the experimental
framework. This custom improver will allow you to optimize experiment combinations
based on specific logic and criteria you define. As experiments evolve and grow in
complexity, custom combination improvers like the one you've developed will become
instrumental in achieving more refined and better results.
