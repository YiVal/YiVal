---
sidebar_position: 7
---

# State

##  `ExperimentState`

###   Introduction 

###   Class Definition 

####    Description

   Represents the state of active experiments and their variations. It provides functionality to retrieve the next variation for an experiment, manage and initialize variations, and get all possible combinations of variations.

####    Attributes

- **`active(bool)`**:
  - Indicates if the experiment is currently active.
- **`current_variations(Dict[str, List[Any]])`**:
  - Holds the variations for each experiment.
- **`counters(Dict[str, int])`**:
  - Keeps track of the number of variations used for each experiment.

####    Methods

- **`get_instance() -> ExperimentState`**:  
  - Retrieves the instance of the `ExperimentState`. As it's implemented with a singleton pattern, this method ensures only one instance exists.
- **`get_default_state() -> ExperimentState`**: 
  -  Retrieves the default state instance of the `ExperimentState`.
- **`get_next_variation(name: str) -> Optional[Any]`**:  
  - Retrieves the next variation for a given experiment name.
- **`get_all_variation_combinations() -> List[Dict[str, Any]]`**:  
  - Provides all possible combinations of the variations across all experiments.
- **`initialize_variations_from_config()`**:  
  - Initializes the variations for the experiments based on the provided `ExperimentConfig`.
- **`set_variations_for_experiment(name: str, variations: Union[List[Any], Iterator[Any]])`**: 
  - Sets the variations for a given experiment name.
- **`clear_variations_for_experiment()`**:  
  - Clears all the variations associated with the experiments.
- **`set_experiment_config(config: Any)`**:  
  - Sets the `ExperimentConfig` and initializes the variations accordingly.
- **`set_specific_variation(name: str, variation: Any)`**:  
  - Assigns a specific variation to an experiment without cycling through the available variations.

###   Example

**Initialize**: Create an instance of the `ExperimentState`.

```Python
     state = ExperimentState.get_instance()
```

**Set Experiment Config**: Before retrieving variations, you need to set the experiment configuration. 

```Python
   state.set_experiment_config(your_experiment_config)
```

**Retrieve Variations**: Get the next variation for an experiment.

```Python
   variation = state.get_next_variation('experiment_name')
```

**All Variation Combinations**: To get all possible combinations of variations across experiments:

```Python
 combinations = state.get_all_variation_combinations()
```
