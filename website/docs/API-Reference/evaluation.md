---
sidebar_position: 4
---
# Evaluation

## `BaseEvaluator`

### Introduction

### Class Definition

#### Description

   Evaluators are central components in the experimental framework that interpret experiment results and offer either quantitative or qualitative feedback.

#### Attributes

### Example

### [Source Code](https://github.com/YiVal/YiVal/blob/master/src/yival/evaluators/base_evaluator.py)

## `EvaluatorType`

### Introduction

### Class Definition

#### Description

   The `EvaluatorType` enumeration class delineates the various evaluation methodologies available within the evaluator's module. Each type signifies a distinct approach to model assessment.

#### Values

- **`INDIVIDUAL`**:
    - This evaluation type signifies that each model or output is evaluated on its own merit, without considering other variations or examples.
- **`COMPARISON`**:
    - In this evaluation type, one specific example is given, and models or outputs are compared based on how they handle that particular example.
- **`ALL`**:
    - This type indicates a comprehensive evaluation approach, where all available examples are considered. Each model or output is evaluated across the entirety of the provided dataset, giving a holistic view of its performance.

### Example

## `AlpacaEvalEvaluator`

### Introduction

  The `AlpacaEvalEvaluator` class is designed to facilitate evaluations using the Alpaca Eval system. This system is employed to rank different model outputs based on human evaluations. The specific implementation interfaces with the OpenAI API to carry out these evaluations, ensuring a blend of automation with human-like discernment.

### Class Definition

#### Description

   Tailored for the `AlpacaEvalEvaluator`, this configuration class sets the guidelines and parameters for the evaluation process.

#### Attributes

- **`alpaca_annotator_name(str)`**:
    - Specifies the Alpaca Eval annotator to be used. The default value is `"alpaca_eval_gpt4"`.
- **`matching_technique(MatchingTechnique)`**:
    - Determines the technique used for matching during the evaluation. The default value is `MatchingTechnique.MATCH`.

### Example

#### Evaluating Sample Data with Alpaca Evaluator

```Python
# Creating a configuration for AlpacaEvalEvaluator
evaluator_config = AlpacaEvalEvaluatorConfig(
    name="alpaca_eval_evaluator",
    alpaca_annotator_name="alpaca_eval_gpt4",
    evaluator_type=EvaluatorType.COMPARISON
)

# Initializing the evaluator with the given configuration
evaluator = AlpacaEvalEvaluator(evaluator_config)

# Sample data for assessment
sample_group_data = [...]  # A list of ExperimentResult objects

# Evaluating the sample data
evaluator.evaluate_comparison(sample_group_data)

# Printing the evaluation results
for experiment in sample_group_data:
    print(experiment.evaluator_outputs)
```

#### Use Alpaca Evaluator in the YiVal config

```YAML
evaluators:
  - evaluator_type: comparison
    alpaca_annotator_name: alpaca_eval_gpt4
    metric_calculators:
      - method: AVERAGE
    name: alpaca_eval_evaluator
```

### [Source Code](https://github.com/YiVal/YiVal/blob/master/src/yival/evaluators/alpaca_eval_evaluator.py)

## `BertScoreEvaluator`

### Introduction

  BERTScore is an evaluation metric for language models based on the BERT language model. Instead of relying solely on token matching, BERTScore leverages the contextual embeddings from BERT to match words in the candidate and reference sentences using cosine similarity. This makes it robust against paraphrasing, allowing it to effectively gauge the semantic similarity between two sentences. Its strong correlation with human judgment, both on sentence-level and system-level evaluations, makes it an attractive metric for various NLP tasks.

### `BertScoreEvaluatorConfig`

#### Description

   Configuration class for the `BertScoreEvaluator`. It specifies various parameters that dictate how the evaluation using BERTScore will be performed.

#### Attributes

- **`evaluator_type`**:
    - Specifies the type of evaluation. In the context of the `BertScoreEvaluator`, it's set to `EvaluatorType.INDIVIDUAL`, meaning each model output is evaluated individually against its corresponding expected result.
    - The default value is `EvaluatorType.INDIVIDUAL`.
- **`description`**:
    - A descriptive text providing additional context or details about the evaluator.
    - The default value is  `"This is the description of the evaluator"`.
- **`lan`**:
    - Language of the text being evaluated. BERTScore uses this to select the appropriate pre-trained BERT model. For instance, 'zh' corresponds to Chinese.
    - The default value is `'zh'`.
- **`indicator`**:
    - Specifies which score to return out of precision (`p`), recall (`r`), or F1 score (`f`).
    - The default value is precision or `'p'`.
- **`name`**:
    - Name of the evaluator.
- **`display_name`**:
    - Display name for the metric.
- **`lan`**:
    - Language of the text being evaluated. BERTScore uses this to select the appropriate pre-trained BERT model.
- **`metric_calculators`**:
    - List of additional metric calculators to be applied.

### Example

  In the usage example below, the evaluator is set up to compute the F1 BERTScore for a model's translation against the expected translation.

```Python
evaluator_config = BertScoreEvaluatorConfig(
    name="bertscore_evaluator",
    display_name="bertscore",
    lan="en",
    indicator="f",
    metric_calculators=[]
)

input_data_example = InputData(
    content={
        "instruction": "Translate the sentence to English.",
    },
    expected_result="Have a great day!"
)

experiment_result_example = ExperimentResult(
    input_data=input_data_example,
    combination={
        "wrapper1": "var1",
        "wrapper2": "var2"
    },
    raw_output=MultimodalOutput(text_output="Have a nice day!"),
    latency=30.0,
    token_usage=20
)

evaluator = BertScoreEvaluator(evaluator_config)
result = evaluator.evaluate(experiment_result_example)
print(result)
```

### [Source Code](https://github.com/YiVal/YiVal/blob/master/src/yival/evaluators/bertscore_evaluator.py)

## `OpenAIEloEvaluator`

### Introduction

  This module provides an implementation of the ELO-based evaluation system in the `OpenAIEloEvaluator` class. The ELO system ranks different model outputs based on human evaluations. This specific implementation interfaces with the OpenAI API to conduct those evaluations.

### Class Definition

#### Description

   Configuration class for the `OpenAIEloEvaluator`. It specifies various parameters that dictate how the evaluation using the ELO system interfacing with OpenAI will be performed.

#### Attributes

- **`openai_model_name`**:
    - Specifies which OpenAI model to use for the evaluation.
    - The default is set to use the `"gpt-4"` model.
- **`input_description`**:
    - Provides a description of the input data that will be evaluated. This can be utilized when presenting data to the OpenAI model for ranking.

### Example

#### Creating the `OpenAIEloEvaluator`Config File

```Python
    evaluator = OpenAIEloEvaluator(
        OpenAIEloEvaluatorConfig(
            name="openai_elo_evaluator",
            input_description="Translate the given English sentence to French",
            evaluator_type=EvaluatorType.ALL,
        )
    )
    experiment = create_test_data_v2()
    evaluator.evaluate_based_on_all_results([experiment])
    print(experiment)
```

#### Use BertScoreEvaluator in YiVal Config

```YAML
evaluators:
  - evaluator_type: all
    input_description:
      Given an tech startup business, generate one corresponding landing
      page headline
    metric_calculators: []
    name: openai_elo_evaluator
    model_name: gpt-4
```

### [Source Code](https://github.com/YiVal/YiVal/blob/master/src/yival/evaluators/openai_elo_evaluator.py)

## `PythonValidationEvaluator`

### Introduction

  Evaluates the raw output of an experiment by attempting to execute it as Python code. If the code executes without any errors, a positive result is returned. Otherwise, a negative result is returned.

### Class Definition

#### Description

   Configuration class for the `PythonValidationEvaluator`. It specifies the matching technique to be used for the evaluation.

#### Attributes

- **`matching_technique`**:
    - The default value is `MatchingTechnique.MATCH`.

### Example

```YAML
evaluators:
  - evaluator_type: individual
    matching_technique: includes
    metric_calculators:
      - method: AVERAGE
    name: python_validation_evaluator
```

### [Source Code](https://github.com/YiVal/YiVal/blob/master/src/yival/evaluators/python_validation_evaluator.py)

## `RougeEvaluator`

### Introduction

  The Rouge Evaluator is an advanced tool tailored for assessing the quality of dialogue model outputs. Leveraging the ROUGE (Recall-Oriented Understudy for Gisting Evaluation) metric, this evaluator emphasizes the relevance, coherence, and fluency of the generated content. Designed specifically for dialogue systems, the Rouge Evaluator offers developers and researchers a refined measure to gauge their model's efficiency, ensuring continuous improvement.

### Class Definition

#### Description

   Configuration class for the `RougeEvaluator`. It specifies the type of ROUGE metric to be used for the evaluation.

#### Attributes

- **`evaluator_type`**:
    - Specifies that the evaluator assesses each experiment individually.
    - The default value is `EvaluatorType.INDIVIDUAL`.
- **`description`**:
    - A brief description of the evaluator.
    - The default value is `"This is the description of the evaluator"`.
- **`rough_type`**:
    - Specifies which type of ROUGE metric to use (e.g., "rouge-1", "rouge-2", "rouge-L").
    - The default value is `"rouge-1"`.

### Example

```Python
import RougeEvaluator, RougeEvaluatorConfig
import ExperimentResult

experiment_result = ExperimentResult(
    # ... your experiment result details here ...
)
config = RougeEvaluatorConfig()
evaluator = RougeEvaluator(config)
output = evaluator.evaluate(experiment_result)
print(output)
```

### [Source Code](https://github.com/YiVal/YiVal/blob/master/src/yival/evaluators/rouge_evaluator.py)

## `StringExpectedResultEvaluator`

### Introduction

  The String Expected Result Evaluator introduces a specialized class designed for evaluating expected results that are strings. This class extends the foundational evaluator and is equipped to compare actual and expected outputs using various matching techniques. The primary goal is to determine the accuracy of the generated strings in comparison to the expected outputs.

### Class Definition

#### Description

   This class extends the BaseEvaluator and provides specific implementation for evaluating string expected results using different matching techniques.

#### Attributes

### Example

#### UseStringExpectedResult in YiVal Config

```YAML
evaluators:
  - evaluator_type: individual
    matching_technique: includes
    metric_calculators:
      - method: AVERAGE
    name: string_expected_result
```

### [Source Code](https://github.com/YiVal/YiVal/blob/master/src/yival/evaluators/string_expected_result_evaluator.py)

## Custom Evaluator Guide: `SimpleEvaluator`

### Introduction

  Evaluators are central components in the experimental framework that interpret experiment results and offer either quantitative or qualitative feedback. This guide will walk you through the steps of creating a custom evaluator, named `SimpleEvaluator`, which returns a value of 1 if the result is 1, and 0 otherwise.

### Creating the SimpleEvaluator Configuration

  Before creating the evaluator, we define the configuration for our `SimpleEvaluator`. The configuration helps in defining how the evaluator should behave and what parameters it may require.

```Python
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

### Implementing the SimpleEvaluator

  Now, let's create the `SimpleEvaluator` that utilizes the above configuration:

```Python
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

### Config

  Next you can config the evaluator

```YAML
custom_evaluators:
  simple_evaluator:
    class: /path/to/simple_evaluator.SimpleEvaluator
    config_cls: /path/to/simple_evaluator_config.SimpleEvaluatorConfig
```

  And use it

```YAML
evaluators:
  - name: simple_evaluator
    simple_evaluator:
      metric_calculators: []
```

### Conclusion

  By following this guide, you've successfully developed, configured, and registered  a custom evaluator named `SimpleEvaluator` within the experimental framework.  Custom evaluators, like the one you've created, enable a tailored approach to interpreting and analyzing experiment results, ensuring the specific needs of an experiment are met.
