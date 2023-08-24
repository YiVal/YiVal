# Custom Selection Strategy Creation Guide

## Introduction

Selection strategies are paramount in the experimental framework, guiding the
selection or prioritization of experiments, scenarios, or configurations. These
strategies can be based on a variety of criteria, ranging from past performance
to specific business rules. In this guide, we'll outline the process for creating
your own custom selection strategy.

## Table of Contents

1. Introduction
2. The Essence of Selection Strategy
3. Crafting a Custom Selection Strategy
4. Registering Your Custom Strategy
5. Conclusion

## The Essence of Selection Strategy

The `SelectionStrategy` class is the backbone of all selection strategies. It
encapsulates core methods to:

- Register new selection strategies.
- Retrieve registered strategies.
- Access their default configurations.

At its core, a selection strategy's primary task is to decide how to select or
prioritize specific experiments or configurations.

## Crafting a Custom Selection Strategy

To devise a custom selection strategy, you should inherit from the `SelectionStrategy`
class and implement the `select` abstract method:

```python

class CustomSelectionStrategy(SelectionStrategy):
    """
    Custom strategy for selecting experiments.
    """

    def select(self, experiment):
        """
        Custom logic for selecting or prioritizing experiments.

        Args:
            experiment (Experiment): The experiment under consideration.

        Returns:
            SelectionOutput: The result of the selection process.
        """

        # Your selection logic goes here
        pass
```

## Config

```yml

custom_selection_strategies:
  custom_selection_strategy:
    class: /path/to/custom_selection_strategy.CustomSelectionStrategy
    config_cls: /path/to/custom_selection_strategy.CustomSelectionStrategyConfig

```

To use it

```yml

selection_strategy:
  custom_selection_strategies:
    
```
