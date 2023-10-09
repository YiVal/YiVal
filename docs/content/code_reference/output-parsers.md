<a id="yival.output_parsers.base_parser"></a>

# yival.output\_parsers.base\_parser

<a id="yival.output_parsers.base_parser.BaseParserWithRegistry"></a>

## BaseParserWithRegistry Objects

```python
class BaseParserWithRegistry()
```

Base class for parsers that provides automatic registration of subclasses.
Any subclass that inherits from this base class will be automatically added
to the registry. The registry can then be used to retrieve a parser class
based on its name.

<a id="yival.output_parsers.base_parser.BaseParserWithRegistry.registry"></a>

#### registry

Class-level registry for all parser subclasses

<a id="yival.output_parsers.base_parser.BaseParserWithRegistry.__init_subclass__"></a>

#### \_\_init\_subclass\_\_

```python
def __init_subclass__(cls, **kwargs)
```

Automatically called when a subclass is defined.

<a id="yival.output_parsers.base_parser.BaseParserWithRegistry.parse"></a>

#### parse

```python
def parse(output: str) -> List[str]
```

Parse the provided output.
This method should be overridden by subclasses to provide custom
parsing logic.

<a id="yival.output_parsers.utils"></a>

# yival.output\_parsers.utils

<a id="yival.output_parsers.utils.capture_and_parse_with_base_registry"></a>

#### capture\_and\_parse\_with\_base\_registry

```python
def capture_and_parse_with_base_registry(config=None)
```

Decorator to capture stdout of a function and parse it using a specified
parser.

The parser is determined based on the provided configuration. If the
specified parser is not found in the BaseParserWithRegistry's registry,
the function's output will not be captured or parsed.

**Arguments**:

  - config (dict, optional): Configuration dict with 'parser' key specifying
  the parser class name.
  

**Returns**:

  - Decorated function that captures and parses its stdout.

