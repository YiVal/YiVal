<a id="yival.result_selectors.normalize_func"></a>

# yival.result\_selectors.normalize\_func

Normalization functions

<a id="yival.result_selectors.normalize_func.min_max_normalization"></a>

#### min\_max\_normalization

```python
def min_max_normalization(matrix: np.ndarray) -> np.ndarray
```

normalize matrix in min_max method

<a id="yival.result_selectors.normalize_func.z_score_normalizatioin"></a>

#### z\_score\_normalizatioin

```python
def z_score_normalizatioin(matrix: np.ndarray) -> np.ndarray
```

normalize matrix in z_score method

<a id="yival.result_selectors.selection_strategy"></a>

# yival.result\_selectors.selection\_strategy

Selection Strategy Module.

This module defines an abstract base class for selection strategies.
A selection strategy 
determines how to select or prioritize specific experiments, scenarios, or
configurations based on certain criteria.

<a id="yival.result_selectors.selection_strategy.SelectionStrategy"></a>

## SelectionStrategy Objects

```python
class SelectionStrategy(ABC)
```

Abstract base class for selection strategies.

<a id="yival.result_selectors.selection_strategy.SelectionStrategy.get_strategy"></a>

#### get\_strategy

```python
@classmethod
def get_strategy(cls, name: str) -> Optional[Type['SelectionStrategy']]
```

Retrieve strategy class from registry by its name.

<a id="yival.result_selectors.selection_strategy.SelectionStrategy.get_default_config"></a>

#### get\_default\_config

```python
@classmethod
def get_default_config(cls, name: str) -> Optional[BaseConfig]
```

Retrieve the default configuration of a strategy by its name.

<a id="yival.result_selectors.selection_context"></a>

# yival.result\_selectors.selection\_context

<a id="yival.result_selectors.ahp_selection"></a>

# yival.result\_selectors.ahp\_selection

