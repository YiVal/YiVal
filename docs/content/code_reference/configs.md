<a id="yival.schemas.common_structures"></a>

# yival.schemas.common\_structures

<a id="yival.schemas.common_structures.InputData"></a>

## InputData Objects

```python
@dataclass
class InputData()
```

Represents the input data for an experiment example.

**Attributes**:

  - example_id Optional[str]: A unique identifier for the example.
  - content (Dict[str, Any]): A dictionary that contains all the necessary input
  parameters for the custom function.
  - expected_result (Optional[Any]): The expected result given the input.

<a id="yival.schemas.experiment_config"></a>

# yival.schemas.experiment\_config

Module for experiment configuration structures.

This module provides data structures to capture configurations required to run an
experiment.

<a id="yival.schemas.experiment_config.WrapperVariation"></a>

## WrapperVariation Objects

```python
@dataclass
class WrapperVariation()
```

Represents a variation within a wrapper.
The value can be any type, but typical usages might include strings, 
numbers, configuration dictionaries, or even custom class configurations.

<a id="yival.schemas.experiment_config.WrapperVariation.value_type"></a>

#### value\_type

e.g., "string", "int", "float", "ClassA", ...

<a id="yival.schemas.experiment_config.WrapperVariation.value"></a>

#### value

The actual value or parameters to initialize a value

<a id="yival.schemas.experiment_config.WrapperVariation.instantiate"></a>

#### instantiate

```python
def instantiate() -> Any
```

Returns an instantiated value based on value_type and params.

<a id="yival.schemas.experiment_config.WrapperConfig"></a>

## WrapperConfig Objects

```python
@dataclass
class WrapperConfig()
```

Configuration for each individual wrapper used in the experiment.

<a id="yival.schemas.experiment_config.OutputConfig"></a>

## OutputConfig Objects

```python
@dataclass
class OutputConfig()
```

Configuration for experiment output.

**Attributes**:

  - path (str): Path where the experiment output should be saved.
  - formatter (Callable): Function to format the output.

<a id="yival.schemas.experiment_config.ComparisonOutput"></a>

## ComparisonOutput Objects

```python
@dataclass
class ComparisonOutput()
```

Result of a comparison evaluation.

**Attributes**:

  - better_output (str): Name of the wrapper that produced the better output.
  - reason (str): Reason or metric based on which the decision was made.

<a id="yival.schemas.experiment_config.HumanRating"></a>

## HumanRating Objects

```python
@dataclass
class HumanRating()
```

Human rating for an output.

**Attributes**:

  - aspect (str): Aspect being rated.
  - rating (float): Rating value.
  - scale (Tuple[float, float]): Minimum and maximum value of the rating scale.

<a id="yival.schemas.experiment_config.HumanRating.scale"></a>

#### scale

Default scale from 1 to 5

<a id="yival.schemas.experiment_config.Metric"></a>

## Metric Objects

```python
@dataclass
class Metric()
```

Represents a metric calculated from evaluator outputs.

**Attributes**:

  - name (str): Name of the metric (e.g., "accuracy").
  - value (float): Calculated value of the metric.
  - description (Optional[str]): Description or details about the metric.

<a id="yival.schemas.experiment_config.ExperimentSummary"></a>

## ExperimentSummary Objects

```python
@dataclass
class ExperimentSummary()
```

Represents the summary of an entire experiment.

**Attributes**:

  - aggregated_metrics (Dict[str, Dict[str, Metric]]):
  A dictionary where keys are evaluator names and values are dictionaries mapping metric names to their values.
  - ... (other summary attributes)

<a id="yival.schemas.experiment_config.MultimodalOutput"></a>

## MultimodalOutput Objects

```python
@dataclass
class MultimodalOutput()
```

Multimodal output that can include a string, a PIL Image, or both.

**Attributes**:

  - text_output (str): Text output for this example.
  - image_output (PIL.Image.Image): Image output for this example.

<a id="yival.schemas.experiment_config.ExperimentResult"></a>

## ExperimentResult Objects

```python
@dataclass
class ExperimentResult()
```

Result for a single example based on a specific combination of active variations
across wrappers.

**Attributes**:

  - combination (Dict[str, str]): The combination of wrapper names and their active
  variation_ids for this example.
  - raw_output (Any): Raw output for this example. Support str and PILimage
  - latency (float): Latency for producing the output for this example
  (in milliseconds or appropriate unit).
  - token_usage (int): Number of tokens used for this example.
  - evaluator_outputs (List[EvaluatorOutput]): Evaluator outputs for this example.
  - human_rating (Optional[HumanRating]): Human rating for this example.
  - intermediate_logs (List[str]): Logs captured during the experiment.

<a id="yival.schemas.experiment_config.FunctionMetadata"></a>

## FunctionMetadata Objects

```python
@dataclass
class FunctionMetadata()
```

<a id="yival.schemas.experiment_config.FunctionMetadata.parameters"></a>

#### parameters

[(param_name, description), ...]

<a id="yival.schemas.experiment_config.Experiment"></a>

## Experiment Objects

```python
@dataclass
class Experiment()
```

Represents an entire experiment.

<a id="yival.schemas.selector_strategies"></a>

# yival.schemas.selector\_strategies

<a id="yival.schemas.dataset_config"></a>

# yival.schemas.dataset\_config

<a id="yival.schemas.dataset_config.DatasetSourceType"></a>

## DatasetSourceType Objects

```python
class DatasetSourceType(Enum)
```

Enum to specify the source of dataset: USER, DATASET, or MACHINE_GENERATED.

<a id="yival.schemas.dataset_config.DatasetConfig"></a>

## DatasetConfig Objects

```python
@dataclass
class DatasetConfig()
```

Configuration for the dataset used in the experiment.

**Attributes**:

  - source_type (DatasetSourceType): Source of dataset, either directly from the user,
  from a dataset, or machine-generated.
  - file_path (Union[str, None]): Path to the dataset file. Relevant only if
  source_type is DATASET.
  - reader (Union[str, None]): Class name to process the dataset file.
  Relevant only if source_type is DATASET.
  - reader_config (Union[BaseReaderConfig, None]): Configuration for the reader.
  - output_path (Union[str, None]): Path to store the machine-generated data. Relevant
  only if source_type is MACHINE_GENERATED.
  - data_generators (Optional[Dict[str, BaseDataGeneratorConfig]]): List of data_generators to generate data.
  Relevant only if source_type is MACHINE_GENERATED.

<a id="yival.schemas.combination_improver_configs"></a>

# yival.schemas.combination\_improver\_configs

<a id="yival.schemas.combination_improver_configs.BaseCombinationImproverConfig"></a>

## BaseCombinationImproverConfig Objects

```python
@dataclass
class BaseCombinationImproverConfig()
```

Base configuration class for all combination improvers.

<a id="yival.schemas.evaluator_config"></a>

# yival.schemas.evaluator\_config

<a id="yival.schemas.evaluator_config.MethodCalculationMethod"></a>

## MethodCalculationMethod Objects

```python
class MethodCalculationMethod(Enum)
```

Configuration for metric calculation method.

<a id="yival.schemas.evaluator_config.MetricCalculatorConfig"></a>

## MetricCalculatorConfig Objects

```python
@dataclass
class MetricCalculatorConfig()
```

Configuration for metric calculation.

<a id="yival.schemas.evaluator_config.BaseEvaluatorConfig"></a>

## BaseEvaluatorConfig Objects

```python
@dataclass
class BaseEvaluatorConfig()
```

Base configuration for evaluators.

<a id="yival.schemas.evaluator_config.EvaluatorConfig"></a>

## EvaluatorConfig Objects

```python
@dataclass
class EvaluatorConfig(BaseEvaluatorConfig)
```

Configuration for custom evaluator.

<a id="yival.schemas.evaluator_config.ComparisonEvaluatorConfig"></a>

## ComparisonEvaluatorConfig Objects

```python
@dataclass
class ComparisonEvaluatorConfig(BaseEvaluatorConfig)
```

Configuration for evaluators that compare different outputs.

<a id="yival.schemas.evaluator_config.GlobalEvaluatorConfig"></a>

## GlobalEvaluatorConfig Objects

```python
@dataclass
class GlobalEvaluatorConfig(BaseEvaluatorConfig)
```

Configuration for evaluators that compare based on all outputs.

<a id="yival.schemas.evaluator_config.EvaluatorOutput"></a>

## EvaluatorOutput Objects

```python
@dataclass
class EvaluatorOutput()
```

Result of an evaluator.

<a id="yival.schemas.evaluator_config.BertScoreEvaluatorConfig"></a>

## BertScoreEvaluatorConfig Objects

```python
@dataclass
class BertScoreEvaluatorConfig(EvaluatorConfig)
```

<a id="yival.schemas.evaluator_config.BertScoreEvaluatorConfig.indicator"></a>

#### indicator

p,r,f

<a id="yival.schemas.reader_configs"></a>

# yival.schemas.reader\_configs

<a id="yival.schemas.reader_configs.BaseReaderConfig"></a>

## BaseReaderConfig Objects

```python
@dataclass
class BaseReaderConfig()
```

Base configuration class for all readers.

<a id="yival.schemas.reader_configs.CSVReaderConfig"></a>

## CSVReaderConfig Objects

```python
@dataclass
class CSVReaderConfig(BaseReaderConfig)
```

Configuration specific to the CSV reader.

<a id="yival.schemas.wrapper_configs"></a>

# yival.schemas.wrapper\_configs

<a id="yival.schemas.wrapper_configs.BaseWrapperConfig"></a>

## BaseWrapperConfig Objects

```python
@dataclass
class BaseWrapperConfig()
```

Base configuration class for wrappers.

<a id="yival.schemas.wrapper_configs.StringWrapperConfig"></a>

## StringWrapperConfig Objects

```python
@dataclass
class StringWrapperConfig(BaseWrapperConfig)
```

Configuration specific to the StringWrapper.

<a id="yival.schemas.model_configs"></a>

# yival.schemas.model\_configs

<a id="yival.schemas.model_configs.ModelProvider"></a>

## ModelProvider Objects

```python
@dataclass
class ModelProvider()
```

Represents the details required to interact with a GebAI model.

**Arguments**:

- `api_key` _str_ - The API key used for authenticating requests to the
  model provider.
- `provider_name` _str_ - Name of the model provider.

<a id="yival.schemas.model_configs.Request"></a>

## Request Objects

```python
@dataclass
class Request()
```

Represents the information needed to make an inference request to a
GenAI model.

**Arguments**:

- `model_name` _str_ - The name of the machine learning model to be used
  for inference.
- `params` _Dict[str, Any]_ - Additional parameters to configure the model
  for inference.
- `prompt` _Union[str, List[Dict[str, str]]]_ - The input prompt or set of
  prompts to use for the inference.
  Can be a simple string or a list of dictionaries, each containing
  key-value pairs for more complex prompt structures.

<a id="yival.schemas.model_configs.Response"></a>

## Response Objects

```python
@dataclass
class Response()
```

Represents the outcome of an inference request.

**Arguments**:

- `output` _Any_ - The result generated by the GenAI model,
  which can be of any type depending on the model and task.

<a id="yival.schemas.model_configs.CallOption"></a>

## CallOption Objects

```python
@dataclass
class CallOption()
```

Represents call options with llm

**Arguments**:

- `temperature` _float_ - hyperparameter that
  controls the randomness of predictions by scaling the logits
  before applying softmax.
  
  presence_penalty (float)

<a id="yival.schemas.varation_generator_configs"></a>

# yival.schemas.varation\_generator\_configs

<a id="yival.schemas.varation_generator_configs.BaseVariationGeneratorConfig"></a>

## BaseVariationGeneratorConfig Objects

```python
@dataclass
class BaseVariationGeneratorConfig()
```

Base configuration class for all variation generators.

<a id="yival.schemas.varation_generator_configs.OpenAIPromptBasedVariationGeneratorConfig"></a>

## OpenAIPromptBasedVariationGeneratorConfig Objects

```python
@dataclass
class OpenAIPromptBasedVariationGeneratorConfig(BaseVariationGeneratorConfig)
```

Generate variation using chatgpt. Currently only support openai models.

<a id="yival.schemas.data_generator_configs"></a>

# yival.schemas.data\_generator\_configs

<a id="yival.schemas.data_generator_configs.BaseDataGeneratorConfig"></a>

## BaseDataGeneratorConfig Objects

```python
@dataclass
class BaseDataGeneratorConfig()
```

Base configuration class for all data generators.

<a id="yival.schemas.data_generator_configs.OpenAIPromptBasedGeneratorConfig"></a>

## OpenAIPromptBasedGeneratorConfig Objects

```python
@dataclass
class OpenAIPromptBasedGeneratorConfig(BaseDataGeneratorConfig)
```

Generate test cases from prompt. Currently only support openai models.

<a id="yival.schemas.trainer_configs"></a>

# yival.schemas.trainer\_configs

<a id="yival.schemas.trainer_configs.BaseTrainerConfig"></a>

## BaseTrainerConfig Objects

```python
@dataclass
class BaseTrainerConfig()
```

Base configuration class for all trainers

<a id="yival.schemas.trainer_configs.LoRAConfig"></a>

## LoRAConfig Objects

```python
@dataclass
class LoRAConfig()
```

LoRA config for SFT Trainer

<a id="yival.schemas.trainer_configs.TrainArguments"></a>

## TrainArguments Objects

```python
@dataclass
class TrainArguments()
```

Train Arguments in trl trainer
Parameters for training arguments details => https://github.com/huggingface/transformers/blob/main/src/transformers/training_args.py#L158

<a id="yival.schemas.trainer_configs.SFTTrainerConfig"></a>

## SFTTrainerConfig Objects

```python
@dataclass
class SFTTrainerConfig(BaseTrainerConfig)
```

Supervised Fine-tuning trainer config

