---
sidebar_position: 6

---

# Selection 

##  `SelectionStrategy`

###   Introduction 

  This module defines an abstract base class for selection strategies. A selection strategy determines how to select or prioritize specific experiments, scenarios, or configurations based on certain criteria.

###   Class Definition 

####    Description

####    Attributes



###   Example

###  [Source Code](https://github.com/YiVal/YiVal/blob/master/src/yival/result_selectors/selection_strategy.py)

##  `AHPSelectionStrategy`

###   Introduction 

  This module provides the `AHPSelection` class, which is a selection strategy based on the Analytic Hierarchy Process (AHP). The strategy uses the provided criteria, their weights, and data from the experiment to rank the experiment combinations and select the best one.

###   Class Definition 

####    Description

   A data class defining the configuration for the AHPSelection strategy.

####    Attributes

- **`criteria(List[str])`**: 
  - A list of criteria names to be considered during selection.
- **`criteria_weights(Dict[str, float])`**: 
  - A dictionary mapping each criterion to its weight.
- **`criteria_maximization(Dict[str, bool])`**: 
  - A dictionary indicating whether each criterion should be maximized (True) or minimized (False).
- **`normalize_func(Optional[str])`**: 
  - The name of the normalization function to be used, if any.

###   Example

####    AHPSelection Configuration 

```Python
    combination_A = CombinationAggregatedMetrics(
        combo_key=str({"name": "A"}),
        experiment_results=[],
        aggregated_metrics={},
        average_token_usage=120,
        average_latency=200,
        combine_evaluator_outputs=[EvaluatorOutput(name="elo", result=1500)]
    )

    # Combination B has a lower elo, but also much lower token usage and
    # latency
    combination_B = CombinationAggregatedMetrics(
        combo_key=str({"name": "B"}),
        experiment_results=[],
        aggregated_metrics={},
        average_token_usage=50,
        average_latency=50,
        combine_evaluator_outputs=[EvaluatorOutput(name="elo", result=1300)]
    )

    #Combination C has highest elo with highest token usage and latency
    combination_C = CombinationAggregatedMetrics(
        combo_key=str({"name": "C"}),
        experiment_results=[],
        aggregated_metrics={},
        average_token_usage=300,
        average_latency=300,
        combine_evaluator_outputs=[EvaluatorOutput(name="elo", result=1600)]
    )

    # The experiment data
    trade_off_test_data = Experiment(
        combination_aggregated_metrics=[
            combination_A, combination_B, combination_C
        ],
        group_experiment_results=[]
    )

    config_trade_off = AHPConfig(
        criteria=["elo", "average_token_usage", "average_latency"],
        criteria_weights={
            "elo": 0.6,
            "average_token_usage": 0.2,
            "average_latency": 0.2
        },
        criteria_maximization={
            "elo": True,
            "average_token_usage": False,
            "average_latency": False
        },
        normalize_func='z-score'
    )
    context_trade_off = SelectionContext(
        strategy=AHPSelection(config=config_trade_off)
    )
    best_combo_trade_off = context_trade_off.execute_selection(
        trade_off_test_data
    )
    print(best_combo_trade_off)
   
```

####    Use OpenAI Prompt Data Generator in the YiVal config

```YAML
selection_strategy:
  ahp_selection:
    criteria:
      - "openai_prompt_based_evaluator: clear"
      - average_token_usage
      - average_latency
    criteria_maximization:
      "openai_prompt_based_evaluator: clear": true
      average_latency: false
      average_token_usage: false
    criteria_weights:
      "openai_prompt_based_evaluator: clear": 0.6
      average_latency: 0.2
      average_token_usage: 0.2
    normalize_func: "z-score"
```

##  Custom Selection Strategy Guide:  `CustomSelectionStrategy` 

###   Introduction

  Selection strategies are paramount in the experimental framework, guiding the selection or prioritization of experiments, scenarios, or configurations. These strategies can be based on a variety of criteria, ranging from past performance to specific business rules. In this guide, we'll outline the process for creating your own custom selection strategy.

###   The Essence of Selection Strategy

  The `SelectionStrategy` class is the backbone of all selection strategies. It encapsulates core methods to:

- Register new selection strategies.
- Retrieve registered strategies.
- Access their default configurations.

  At its core, a selection strategy's primary task is to decide how to select or prioritize specific experiments or configurations.

###   Crafting a Custom Selection Strategy

  To devise a custom selection strategy, you should inherit from the `SelectionStrategy` class and implement the `select` abstract method:

```Python
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

###   Config

```YAML
custom_selection_strategies:
  custom_selection_strategy:
    class: /path/to/custom_selection_strategy.CustomSelectionStrategy
    config_cls: /path/to/custom_selection_strategy.CustomSelectionStrategyConfig
```

  To use it:

```Plaintext
selection_strategy:
  custom_selection_strategies:
```
