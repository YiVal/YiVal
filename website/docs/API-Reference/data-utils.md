---
sidebar_position: 10
---

# Data Utils

## `DataUtils`

### Introduction

### Class Definition

#### Description

#### Methods (Functions)

- **`evaluate_condition(condition: str, evaluator_output: EvaluatorOutput) -> bool`**:

    - Uses the `_tokenize_condition` and `_evaluate_tokenized_condition` functions to evaluate a condition against an evaluator output.

- **`read_code_from_path_or_module(path_or_module: str) -> Optional[str]`**:

    - Reads the source code from either an absolute file path or from a module and its function. Returns the source code if found, otherwise `None`.

- **`transform_experiment_result_generic(code: str, exp_result: ExperimentResult) -> dict`**:
    - Transforms an experiment result into a generic format, where the result is a dictionary containing the `Input` and `Output` fields.

### Example

```Python
    # Read the code from the source
    code = read_code_from_path_or_module("yival.demo.headline_generation")
    import pickle

    from yival.schemas.experiment_config import Experiment
    condition = "name == openai_prompt_based_evaluator AND result >= 3 AND display_name == clarity "
    with open('test_demo_results.pkl', 'rb') as f:
        result: Experiment = pickle.load(f)
    for combo_result in result.combination_aggregated_metrics:
        results: List[ExperimentResult] = combo_result.experiment_results
        for result in results:
            for eo in result.evaluator_outputs:
                condition_met = evaluate_condition(condition, eo)
                if condition_met:
                    # Extract the result pair given code.
                    result_pair = transform_experiment_result_generic(
                        code, result
                    )
                    print(result_pair)
```
