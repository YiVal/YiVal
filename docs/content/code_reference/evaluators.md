<a id="yival.evaluators.base_evaluator"></a>

# yival.evaluators.base\_evaluator

Evaluators Module.

This module contains the base class and common methods for evaluators used in
experiments.
Evaluators are essential components in the system that interpret the results
of experiments and provide quantitative or qualitative feedback. Specific
evaluators are expected to inherit from the base class and implement custom
evaluation logic as needed.

<a id="yival.evaluators.base_evaluator.BaseEvaluator"></a>

## BaseEvaluator Objects

```python
class BaseEvaluator(ABC)
```

Base class for all evaluators.

This class provides the basic structure and methods for evaluators.
Specific evaluators should inherit from this class and implement the
necessary methods.

<a id="yival.evaluators.base_evaluator.BaseEvaluator.__init__"></a>

#### \_\_init\_\_

```python
def __init__(config: BaseEvaluatorConfig)
```

Initialize the evaluator with its configuration.

**Arguments**:

- `config` _BaseEvaluatorConfig_ - The configuration for the evaluator.

<a id="yival.evaluators.base_evaluator.BaseEvaluator.register"></a>

#### register

```python
@classmethod
def register(cls, name: str)
```

Decorator to register new evaluators.

<a id="yival.evaluators.base_evaluator.BaseEvaluator.get_evaluator"></a>

#### get\_evaluator

```python
@classmethod
def get_evaluator(cls, name: str) -> Optional[Type['BaseEvaluator']]
```

Retrieve evaluator class from registry by its name.

<a id="yival.evaluators.base_evaluator.BaseEvaluator.get_default_config"></a>

#### get\_default\_config

```python
@classmethod
def get_default_config(cls, name: str) -> Optional[BaseEvaluatorConfig]
```

Retrieve the default configuration of an evaluator by its name.

<a id="yival.evaluators.base_evaluator.BaseEvaluator.get_config_class"></a>

#### get\_config\_class

```python
@classmethod
def get_config_class(cls, name: str) -> Optional[Type[BaseEvaluatorConfig]]
```

Retrieve the configuration class of a reader by its name.

<a id="yival.evaluators.base_evaluator.BaseEvaluator.evaluate"></a>

#### evaluate

```python
def evaluate(experiment_result: ExperimentResult) -> EvaluatorOutput
```

Evaluate the experiment result and produce an evaluator output.

**Arguments**:

- `experiment_result` _ExperimentResult_ - The result of an experiment
  to be evaluated.
  

**Returns**:

- `EvaluatorOutput` - The result of the evaluation.

<a id="yival.evaluators.base_evaluator.BaseEvaluator.evaluate_comparison"></a>

#### evaluate\_comparison

```python
def evaluate_comparison(group_data: List[ExperimentResult]) -> None
```

Evaluate and compare a list of experiment results.

This method is designed to evaluate multiple experiment results
together, allowing for comparisons and potentially identifying trends,
anomalies, or other patterns in the set of results.

**Arguments**:

- `group_data` _List[ExperimentResult]_ - A list of experiment results
  to be evaluated together.
  

**Notes**:

  Implementations of this method in subclasses should handle the
  specifics of how multiple experiments are evaluated and compared.

<a id="yival.evaluators.base_evaluator.BaseEvaluator.evaluate_based_on_all_results"></a>

#### evaluate\_based\_on\_all\_results

```python
def evaluate_based_on_all_results(experiment: List[Experiment]) -> None
```

Evaluate based on the entirety of experiment results.

This method evaluates an entire list of experiments, potentially taking
into account all available data to produce a comprehensive evaluation.

**Arguments**:

- `experiment` _List[Experiment]_ - A list of all experiments to be
  evaluated.
  

**Notes**:

  Implementations of this method in subclasses should determine how
  to best utilize all available experiment data for evaluation.

<a id="yival.evaluators.bertscore_evaluator"></a>

# yival.evaluators.bertscore\_evaluator

BERTScore is a language model evaluation metric based on the BERT language model. 
It leverages the pre-trained contextual embeddings from BERT and matches words in candidate and reference sentences by cosine similarity. 
It has been shown to correlate with human judgment on sentence-level and system-level evaluation.

<a id="yival.evaluators.bertscore_evaluator.BertScoreEvaluator"></a>

## BertScoreEvaluator Objects

```python
class BertScoreEvaluator(BaseEvaluator)
```

Evaluator calculate bert_score

<a id="yival.evaluators.bertscore_evaluator.BertScoreEvaluator.evaluate"></a>

#### evaluate

```python
def evaluate(experiment_result: ExperimentResult) -> EvaluatorOutput
```

Evaluate the experiment result according to bertsocre

<a id="yival.evaluators.bertscore_evaluator.main"></a>

#### main

```python
def main()
```

Main function to test the bertscore evaluator

<a id="yival.evaluators.alpaca_eval_evaluator"></a>

# yival.evaluators.alpaca\_eval\_evaluator

Elo Evaluators Module.

This module contains the OpenAIEloEvaluator class, which implements an
ELO-based evaluation system. The ELO system is used to rank different model
outputs based on human evaluations, and this specific 
implementation interfaces with the OpenAI API for those evaluations.

<a id="yival.evaluators.openai_elo_evaluator"></a>

# yival.evaluators.openai\_elo\_evaluator

Elo Evaluators Module.

This module contains the OpenAIEloEvaluator class, which implements an
ELO-based evaluation system. The ELO system is used to rank different model
outputs based on human evaluations, and this specific 
implementation interfaces with the OpenAI API for those evaluations.

<a id="yival.evaluators.openai_elo_evaluator.K"></a>

#### K

Elo rating constant

<a id="yival.evaluators.openai_elo_evaluator.OpenAIEloEvaluator"></a>

## OpenAIEloEvaluator Objects

```python
class OpenAIEloEvaluator(BaseEvaluator)
```

OpenAIEloEvaluator is an evaluator that uses the ELO rating system to rank
model outputs.

<a id="yival.evaluators.openai_elo_evaluator.OpenAIEloEvaluator.expected_score"></a>

#### expected\_score

```python
def expected_score(r1, r2)
```

Calculate the expected score between two ratings.

<a id="yival.evaluators.string_expected_result_evaluator"></a>

# yival.evaluators.string\_expected\_result\_evaluator

Module: string_expected_result_evaluator.py

This module defines the StringExpectedResultEvaluator class, which is used for
evaluating string expected results.

Classes:
    StringExpectedResultEvaluator: Class for evaluating string expected
    results.

<a id="yival.evaluators.string_expected_result_evaluator.is_valid_json"></a>

#### is\_valid\_json

```python
def is_valid_json(s: str) -> bool
```

Check if the given string is a valid JSON.

**Arguments**:

- `s` _str_ - The input string to check.
  

**Returns**:

- `bool` - True if the input string is a valid JSON, False otherwise.

<a id="yival.evaluators.string_expected_result_evaluator.StringExpectedResultEvaluator"></a>

## StringExpectedResultEvaluator Objects

```python
class StringExpectedResultEvaluator(BaseEvaluator)
```

Class for evaluating string expected results.

This class extends the BaseEvaluator and provides specific implementation
for evaluating string expected results using different matching techniques.

**Attributes**:

- `config` _ExpectedResultEvaluatorConfig_ - Configuration object for the
  evaluator.

<a id="yival.evaluators.string_expected_result_evaluator.StringExpectedResultEvaluator.__init__"></a>

#### \_\_init\_\_

```python
def __init__(config: ExpectedResultEvaluatorConfig)
```

Initialize the StringExpectedResultEvaluator with the provided
configuration.

**Arguments**:

- `config` _ExpectedResultEvaluatorConfig_ - Configuration object for
  the evaluator.

<a id="yival.evaluators.string_expected_result_evaluator.StringExpectedResultEvaluator.evaluate"></a>

#### evaluate

```python
def evaluate(experiment_result: ExperimentResult) -> EvaluatorOutput
```

Evaluate the expected result against the actual result using the
specified matching technique.

**Returns**:

- `EvaluatorOutput` - An EvaluatorOutput object containing the
  evaluation result.

<a id="yival.evaluators.utils"></a>

# yival.evaluators.utils

<a id="yival.evaluators.utils.fuzzy_match_util"></a>

#### fuzzy\_match\_util

```python
def fuzzy_match_util(generated: str,
                     expected: str,
                     threshold: int = 80) -> bool
```

Matches the generated string with the expected answer(s) using fuzzy
matching.

**Arguments**:

- `generated` _str_ - The generated string.
- `expected` _str_ - The expected answer(s). Can be a string or list of
  strings.
- `threshold` _int, optional_ - The threshold for fuzzy matching. Defaults
  to 80.
  

**Returns**:

- `int` - Returns 1 if there's a match, 0 otherwise.

<a id="yival.evaluators.rouge_evaluator"></a>

# yival.evaluators.rouge\_evaluator

The Rouge Evaluator is an advanced AI tool designed to assess the quality of dialogue models. 
It uses a unique approach to evaluate the responses generated by these models, focusing on aspects 
such as relevance, coherence, and fluency.

This tool is particularly useful for developers and researchers working on dialogue systems, as it
allows them to measure the effectiveness of their models and make necessary improvements. 

The Rouge Evaluator is a valuable asset for anyone looking to enhance the quality 
and performance of their dialogue models.

<a id="yival.evaluators.rouge_evaluator.RougeEvaluator"></a>

## RougeEvaluator Objects

```python
class RougeEvaluator(BaseEvaluator)
```

Evaluator using rouge to calculate rouge score

<a id="yival.evaluators.rouge_evaluator.RougeEvaluator.evaluate"></a>

#### evaluate

```python
def evaluate(experiment_result: ExperimentResult) -> EvaluatorOutput
```

Evaluate the experiment result using rouge evaluat

<a id="yival.evaluators.rouge_evaluator.main"></a>

#### main

```python
def main()
```

Main function to test the rouge evaluator

<a id="yival.evaluators.python_validation_evaluator"></a>

# yival.evaluators.python\_validation\_evaluator

Python Validation Evaluator Module.

This module provides an implementation of the PythonValidationEvaluator,
which evaluates the raw output of an experiment using Python's exec function.
The evaluator is designed to validate Python code snippets and determine
whether they can be executed without any errors.

Classes:
    - PythonValidationEvaluator: Evaluates the raw output of an experiment.

<a id="yival.evaluators.python_validation_evaluator.PythonValidationEvaluator"></a>

## PythonValidationEvaluator Objects

```python
class PythonValidationEvaluator(BaseEvaluator)
```

Python Validation Evaluator.

Evaluates the raw output of an experiment by attempting to execute it as
Python code. If the code executes without any errors, a positive result is
returned. Otherwise, a negative result is returned.

<a id="yival.evaluators.openai_prompt_based_evaluator"></a>

# yival.evaluators.openai\_prompt\_based\_evaluator

OpenAIPromptBasedEvaluator is an evaluator that uses OpenAI's prompt-based
system for evaluations.

The evaluator interfaces with the OpenAI API to present tasks and interpret
the model's responses to determine the quality or correctness of a given
experiment result.

<a id="yival.evaluators.openai_prompt_based_evaluator.extract_choice_from_response"></a>

#### extract\_choice\_from\_response

```python
def extract_choice_from_response(response: str,
                                 choice_strings: Iterable[str]) -> str
```

Extracts the choice from the response string.

<a id="yival.evaluators.openai_prompt_based_evaluator.calculate_choice_score"></a>

#### calculate\_choice\_score

```python
def calculate_choice_score(
        choice: str,
        choice_scores: Optional[Dict[str, float]] = None) -> Optional[float]
```

Calculates the score for the given choice.

<a id="yival.evaluators.openai_prompt_based_evaluator.format_template"></a>

#### format\_template

```python
def format_template(
        template: Union[str, List[Dict[str, str]]],
        content: Dict[str, Any]) -> Union[str, List[Dict[str, str]]]
```

Formats a string or list template with the provided content.

<a id="yival.evaluators.openai_prompt_based_evaluator.choices_to_string"></a>

#### choices\_to\_string

```python
def choices_to_string(choice_strings: Iterable[str]) -> str
```

Converts a list of choices into a formatted string.

<a id="yival.evaluators.openai_prompt_based_evaluator.OpenAIPromptBasedEvaluator"></a>

## OpenAIPromptBasedEvaluator Objects

```python
class OpenAIPromptBasedEvaluator(BaseEvaluator)
```

Evaluator using OpenAI's prompt-based evaluation.

<a id="yival.evaluators.openai_prompt_based_evaluator.OpenAIPromptBasedEvaluator.evaluate"></a>

#### evaluate

```python
def evaluate(experiment_result: ExperimentResult) -> EvaluatorOutput
```

Evaluate the experiment result using OpenAI's prompt-based evaluation.

<a id="yival.evaluators.openai_prompt_based_evaluator.main"></a>

#### main

```python
def main()
```

Main function to test the OpenAIPromptBasedEvaluator.

