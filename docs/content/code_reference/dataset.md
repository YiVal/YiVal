<a id="yival.dataset.data_utils"></a>

# yival.dataset.data\_utils

<a id="yival.dataset.data_utils.read_code_from_path_or_module"></a>

#### read\_code\_from\_path\_or\_module

```python
def read_code_from_path_or_module(path_or_module: str) -> Optional[str]
```

Reads the source code either from an absolute file path or from a module, refined version.

**Arguments**:

  - path_or_module (str): Either an absolute path to a Python file or a module name.
  

**Returns**:

  - Optional[str]: The source code if found, otherwise None.

<a id="yival.dataset.replicate_finetune_utils"></a>

# yival.dataset.replicate\_finetune\_utils

<a id="yival.dataset.replicate_finetune_utils.finetune"></a>

#### finetune

```python
def finetune(input_file: str,
             condition: str,
             custom_function: str,
             destination: str,
             model_name: str,
             num_train_epochs: int = 3,
             support_expected_value: bool = False,
             system_prompt: str = "") -> str
```

Fine-tunes a replicate model using provided data and conditions.

**Arguments**:

  - input_file (str): Path to the input file containing experiment results.
  - condition (str): Condition to evaluate for extracting relevant results.
  - custom_function (str): Path or module containing the custom function used in the experiment.
  - destination: (str): The model to push the trained version to .
  - model_name: (str): Model name that will be used for finetune.
  - num_train_epochs: (int, optional): Number of epochs to train the model.
  - system_prompt (str, optional): System message to prepend to each chat. Defaults to None.
  

**Returns**:

  - str: ID of the fine-tuned model.

<a id="yival.dataset.openai_finetune_utils"></a>

# yival.dataset.openai\_finetune\_utils

<a id="yival.dataset.openai_finetune_utils.finetune"></a>

#### finetune

```python
def finetune(input_file: str,
             condition: str,
             custom_function: str,
             system_prompt: str = "",
             model_suffx: str = "") -> str
```

Fine-tunes a gpt-3.5 using provided data and conditions.

**Arguments**:

  - input_file (str): Path to the input file containing experiment results.
  - condition (str): Condition to evaluate for extracting relevant results.
  - custom_function (str): Path or module containing the custom function used in the experiment.
  - system_prompt (str, optional): System message to prepend to each chat. Defaults to None.
  - model_suffix: (str, optional): Suffix to append to the model name. Defaults to None.
  

**Returns**:

  - str: ID of the fine-tuned model.

