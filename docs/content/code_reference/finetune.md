<a id="yival.finetune.base_trainer"></a>

# yival.finetune.base\_trainer

This module defines the base class for trainer

Trainers are responsible for finetune llms locally based on 
the data and experiment results

<a id="yival.finetune.base_trainer.BaseTrainer"></a>

## BaseTrainer Objects

```python
class BaseTrainer(ABC)
```

Abstract base class for all trainers

**Attributes**:

- `_register` _Dict[str, Dict[str,Any]]_ - A register to keep track of
  trainers
- `default_config` _Optional[BaseTrainerConfig]_ - Default configuration
  for the trainers

<a id="yival.finetune.base_trainer.BaseTrainer.get_trainer"></a>

#### get\_trainer

```python
@classmethod
def get_trainer(cls, name: str) -> Optional[Type['BaseTrainer']]
```

Retrieve trainer class from registry by its name.

<a id="yival.finetune.base_trainer.BaseTrainer.get_default_config"></a>

#### get\_default\_config

```python
@classmethod
def get_default_config(cls, name: str) -> Optional[BaseTrainerConfig]
```

Retrieve the default configuration of a trainer from the name

<a id="yival.finetune.base_trainer.BaseTrainer.register_trainer"></a>

#### register\_trainer

```python
@classmethod
def register_trainer(cls,
                     name: str,
                     trainer_cls: Type['BaseTrainer'],
                     config_cls: Optional[Type[BaseTrainerConfig]] = None)
```

Register a new trainer along with its defualt configuration
and configuration class.

<a id="yival.finetune.base_trainer.BaseTrainer.train"></a>

#### train

```python
@abstractmethod
def train(experiment: Experiment, config: ExperimentConfig) -> TrainerOutput
```

Train models based on the configs and datas

**Arguments**:

- `experiment` _Experiment_ - The experiment with its results.
- `config` _ExperimentConfig_ - The original experiment configuration.
- `evaluator` _Evaluator_ - A utility class to evaluate the
  ExperimentResult. token_logger (TokenLogger): Logs the token usage.
  

**Returns**:

  TrainerOutput

<a id="yival.finetune.sft_trainer"></a>

# yival.finetune.sft\_trainer

This module provides an implementation of Supervised Fine-tuning trainer.

<a id="yival.finetune.sft_trainer.SFTTrainer"></a>

## SFTTrainer Objects

```python
class SFTTrainer(BaseTrainer)
```

SFT Trainer implement

<a id="yival.finetune.back_up_trainer"></a>

# yival.finetune.back\_up\_trainer

This module is the back up trainer

It will only be called when the dependency is not imported correctly

<a id="yival.finetune.utils"></a>

# yival.finetune.utils

<a id="yival.finetune.utils.print_trainable_parameters"></a>

#### print\_trainable\_parameters

```python
def print_trainable_parameters(model)
```

Prints the number of trainable parameters in the model.

