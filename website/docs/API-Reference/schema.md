---
sidebar_position: 1
---
# Schema

## `ExperimentConfig`

### Introduction

  The ExperimentConfig class offers a thorough configuration schema for defining and executing experiments. It encompasses a wide range of experiment components, such as dataset configurations, custom functions, evaluators, trainers, and more.

### Class Definition

#### Description

   The `ExperimentConfig` class outlines the configuration for an experiment, capturing both mandatory and optional parameters.

#### Attributes

- **`description(str)`**:
  - A brief description of the experiment.
- **`dataset(DatasetConfig)`**:
  - The configuration related to the dataset used in the experiment.
- **`custom_function(Optional[str])`**:
  - A custom function for the experiment (if any).
- **`variations(Optional[List[WrapperConfig]])`**:
  - A list of configurations for different variations or wrappers.
- **`selection_strategy(Optional[Dict[str, BaseConfig]])`**:
  - Strategy for selecting specific configurations or variations.
- **`wrapper_configs(Optional[Dict[str, BaseWrapperConfig]])`**:
  - Configuration for specific wrappers.
- **`combinations_to_run(Optional[List[Tuple[str, Any]]])`**:
  - Specific combinations to execute during the experiment.
- **`evaluators(Optional[List[Union[EvaluatorConfig, ComparisonEvaluatorConfig, GlobalEvaluatorConfig]])]`**:
  - Configuration for evaluators that assess the experiment's results.
- **`improver(Optional[BaseCombinationImproverConfig])`**:
  - Configuration for the improver to enhance the combinations.
- **`trainer(Optional[BaseTrainerConfig])`**:
  - Configuration for training models.
- **`output(Optional[OutputConfig])`**:
  - Configuration detailing the experiment's output format and destination.
- **`human_rating_configs(Optional[List[HumanRatingConfig]])`**:
  - Configuration for human raters evaluating the experiment.
- **`existing_experiment_path(Optional[str])`**:
  - Path to a pre-existing experiment (if any).
- **`version(Optional[str])`**:
  - The version of the experiment.
- **`output_parser(Optional[str])`**:
  - Parser for the experiment's output.
- **`metadata(Optional[Dict[str, Any]])`**:
  - Additional metadata related to the experiment.
- **`custom_reader, custom_combination_improver, custom_data_generators, custom_wrappers, custom_evaluators, custom_variation_generators, custom_selection_strategies, custom_improvers(all Optional[Dict[str, Dict[str, Any]]])`**:
  - Custom configurations for various components of the experiment. Each custom attribute allows users to define specific configurations tailored to their requirements.

### Example

```YAML
custom_function: yival.demo.qa.qa
dataset:
  file_path: demo/data/yival_expected_results.csv
  reader: csv_reader
  source_type: dataset
  reader_config:
    expected_result_column: expected_result
description: Configuration fo question answering with expected results.
evaluators:
  - evaluator_type: individual
    matching_technique: includes
    metric_calculators:
      - method: AVERAGE
    name: string_expected_result

variations:
  - name: qa
    variations:
      - instantiated_value: ""
        value: ""
        value_type: str
        variation_id: null
      - instantiated_value: "Think first, then make a decision. Some random thoughts:"
        value: "Think first, then make a decision. Some random thoughts:"
        value_type: str
        variation_id: null
```

### [Source Code](https://security.larksuite.com/link/safety?target=https%3A%2F%2Fgithub.com%2FYiVal%2FYiVal%2Fblob%2Fmaster%2Fsrc%2Fyival%2Fschemas%2Fexperiment_config.py%23L150&scene=ccm&logParams={)

## `InputData`

### Introduction

  The `InputData` class provides a structured representation of individual data samples used in an experiment. It captures essential attributes like the unique identifier, the actual content (input parameters), and the expected result.

### Class Definition

#### Description

   The `InputData` class represents data for a single example in an experiment. It organizes the data into a structured format, making it easier to process and evaluate within the experiment.

#### Attributes

- **`content(Dict[str, Any])`**:
  - A dictionary that encapsulates all the necessary input parameters for a custom function or experiment. This could include features, parameters, or any other required data points.
- **`example_id(Optional[str])`**:
  - A unique identifier for the individual data sample or example. This can be useful for tracking, referencing, or debugging purposes. The default value is `None`.
- **`expected_result(Optional[Any])`**:
  - Represents the expected outcome or result corresponding to the given input. This can be useful for evaluation, comparison, or validation tasks. The default value is `None`.

### Example

```YAML
# Sample data representation using InputData

sample_data = InputData(
    content={
        "feature_1": 5.7,
        "feature_2": 3.2,
        "feature_3": 4.1
    },
    example_id="sample_001",
    expected_result="Class_A"
)

# In this example, `sample_data` represents an individual data point with three features. The expected result for this data sample is "Class_A", and it is uniquely identified by the ID "sample_001".
```

  This documentation offers a comprehensive guide to the `InputData` class. Ensure you adapt the specified content, IDs, results, and other parameters to synchronize with your project's structure and requirements.

### [Source Code](https://github.com/YiVal/YiVal/blob/99585944bf25aee5a694f00af1baff72f3ceb687/src/yival/schemas/common_structures.py#L7)
