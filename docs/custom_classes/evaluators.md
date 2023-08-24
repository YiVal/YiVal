# Custom Evaluator Creation Guide: SimpleEvaluator

## Introduction

Evaluators are central components in the experimental framework that interpret
experiment results and offer either quantitative or qualitative feedback. This
guide will walk you through the steps of creating a custom evaluator, named
`SimpleEvaluator`, which returns a value of 1 if the result is 1, and 0 otherwise.

## Table of Contents

1. Introduction
2. Overview of Base Evaluator
3. Creating the SimpleEvaluator Configuration
4. Implementing the SimpleEvaluator
5. Registering the SimpleEvaluator
6. Conclusion

## Overview of Base Evaluator

The `BaseEvaluator` class provides the foundational structure for all evaluators.
It offers methods to register new evaluators, fetch registered evaluators, and
retrieve their configurations. The primary purpose of evaluators is to interpret
and analyze the results of experiments based on their unique evaluation logic.

## Creating the SimpleEvaluator Configuration

Before creating the evaluator, we define the configuration for our `SimpleEvaluator`.
The configuration helps in defining how the evaluator should behave and what
parameters it may require.

```python
from dataclasses import dataclass, field
from typing import Any, Dict, List

from yival.schemas.evaluator_config import (
    BaseEvaluatorConfig,
    EvaluatorType,
    MetricCalculatorConfig,
)


@dataclass
class SimpleEvaluatorConfig(BaseEvaluatorConfig):
    """
    Configuration for SimpleEvaluator.
    """
    metric_calculators: List[MetricCalculatorConfig] = field(
        default_factory=list
    )
    evaluator_type = EvaluatorType.INDIVIDUAL

    def asdict(self) -> Dict[str, Any]:
        base_dict = super().asdict()
        base_dict["metric_calculators"] = [
            mc.asdict() for mc in self.metric_calculators
        ]
        return base_dict

```

## Implementing the SimpleEvaluator

Now, let's create the `SimpleEvaluator` that utilizes the above configuration:

```python
from simple_evaluator import SimpleEvaluatorConfig
from yival.evaluators.base_evaluator import BaseEvaluator
from yival.schemas.evaluator_config import EvaluatorOutput


@BaseEvaluator.register("simple_evaluator")
class SimpleEvaluator(BaseEvaluator):
    """
    A basic evaluator that returns a value of 1 if the result is 1, and 0
    otherwise.
    """

    def __init__(self, config: SimpleEvaluatorConfig):
        super().__init__(config)

    def evaluate(self, experiment_result) -> EvaluatorOutput:
        """
        Evaluate the experiment result and produce an evaluator output.
        
        Args:
            experiment_result: The result of an experiment to be evaluated.
        
        Returns:
            EvaluatorOutput: The result of the evaluation.
        """
        result = 1 if experiment_result == 1 else 0
        return EvaluatorOutput(name="Simple Evaluation", result=result)

```

## Config

Next you can config the evaluator

```yml
custom_evaluators:
  simple_evaluator:
    class: /path/to/simple_evaluator.SimpleEvaluator
    config_cls: /path/to/simple_evaluator_config.SimpleEvaluatorConfig
```

And use it

```yml
evaluators:
  - name: simple_evaluator
    simple_evaluator:
      metric_calculators: []

```

## Conclusion

By following this guide, you've successfully developed, configured, and registered
 a custom evaluator named `SimpleEvaluator` within the experimental framework.
 Custom evaluators, like the one you've created, enable a tailored approach to
interpreting and analyzing experiment results, ensuring the specific needs of
an experiment are met.
