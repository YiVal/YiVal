<a id="yival.experiment.data_processor"></a>

# yival.experiment.data\_processor

<a id="yival.experiment.data_processor.DataProcessor"></a>

## DataProcessor Objects

```python
class DataProcessor()
```

Utility class to process data based on DatasetConfig.

<a id="yival.experiment.data_processor.DataProcessor.process_data"></a>

#### process\_data

```python
def process_data() -> Iterator[List[InputData]]
```

Processes data based on the DatasetConfig and returns the processed
data.

<a id="yival.experiment.app"></a>

# yival.experiment.app

<a id="yival.experiment.app.utils"></a>

# yival.experiment.app.utils

<a id="yival.experiment.app.utils.image_to_base64"></a>

#### image\_to\_base64

```python
def image_to_base64(image: Image.Image) -> str
```

Converts an image to base64 string.

<a id="yival.experiment.app.hexagram"></a>

# yival.experiment.app.hexagram

<a id="yival.experiment.app.app"></a>

# yival.experiment.app.app

<a id="yival.experiment.app.app.include_image_base64"></a>

#### include\_image\_base64

```python
def include_image_base64(data_dict)
```

Check if a string includes a base64 encoded image.

<a id="yival.experiment.app.app.is_base64_image"></a>

#### is\_base64\_image

```python
def is_base64_image(value)
```

Check if a string is a base64 encoded image.

<a id="yival.experiment.app.app.base64_to_img"></a>

#### base64\_to\_img

```python
def base64_to_img(base64_string)
```

Convert a base64 string into a PIL Image.

<a id="yival.experiment.app.app.extract_and_decode_image_from_string"></a>

#### extract\_and\_decode\_image\_from\_string

```python
def extract_and_decode_image_from_string(data_string)
```

Extract and decode the first image from a string include base64 encoded and return a dictionary.

<a id="yival.experiment.app.app.extract_and_decode_image"></a>

#### extract\_and\_decode\_image

```python
def extract_and_decode_image(data_dict)
```

Extract and decode image from a dictionary include base64 encoded.

<a id="yival.experiment.app.app.create_table"></a>

#### create\_table

```python
def create_table(data)
```

Create an HTML table from a list of dictionaries, where the values can be strings or PIL images.

<a id="yival.experiment.experiment_runner"></a>

# yival.experiment.experiment\_runner

<a id="yival.experiment.experiment_runner.ExperimentRunner"></a>

## ExperimentRunner Objects

```python
class ExperimentRunner()
```

<a id="yival.experiment.experiment_runner.ExperimentRunner.parallel_task"></a>

#### parallel\_task

```python
def parallel_task(data_point, all_combinations, logger, evaluator)
```

Task to be run in parallel for processing data points.

<a id="yival.experiment.experiment_runner.ExperimentRunner.run"></a>

#### run

```python
def run(display: bool = True,
        output_path: Optional[str] = "abc.pkl",
        experiment_input_path: Optional[str] = "abc.pkl",
        async_eval: bool = False)
```

Run the experiment based on the source type and provided configuration.

<a id="yival.experiment.rate_limiter"></a>

# yival.experiment.rate\_limiter

<a id="yival.experiment.utils"></a>

# yival.experiment.utils

<a id="yival.experiment.utils.import_function_from_string"></a>

#### import\_function\_from\_string

```python
def import_function_from_string(func_string: str)
```

Helper function to import a function from a string.

<a id="yival.experiment.utils.get_function_args"></a>

#### get\_function\_args

```python
def get_function_args(func_string: str)
```

Get argument types of a function.

<a id="yival.experiment.utils.call_function_from_string"></a>

#### call\_function\_from\_string

```python
def call_function_from_string(func_string: str, **kwargs) -> Any
```

Call a function specified by a string.

<a id="yival.experiment.evaluator"></a>

# yival.experiment.evaluator

<a id="yival.experiment.evaluator.Evaluator"></a>

## Evaluator Objects

```python
class Evaluator()
```

Utility class to evaluate ExperimentResult.

