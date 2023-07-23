import io
from contextlib import redirect_stdout
from functools import wraps

from .base_parser import BaseParserWithRegistry


def capture_and_parse_with_base_registry(config=None):
    """
    Decorator to capture stdout of a function and parse it using a specified parser.

    The parser is determined based on the provided configuration. If the specified
    parser is not found in the BaseParserWithRegistry's registry, the function's
    output will not be captured or parsed.

    Args:
    - config (dict, optional): Configuration dict with 'parser' key specifying
                               the parser class name.

    Returns:
    - Decorated function that captures and parses its stdout.
    """
    parser_name = config.get("parser", None) if config else None
    parser_instance = None

    if parser_name and parser_name in BaseParserWithRegistry.registry:
        parser_class = BaseParserWithRegistry.registry[parser_name]
        parser_instance = parser_class()

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            if parser_instance:
                f = io.StringIO()
                with redirect_stdout(f):
                    original_output = func(*args, **kwargs)
                captured_output = f.getvalue()
                return original_output, parser_instance.parse(captured_output)
            else:
                original_output = func(*args, **kwargs)
                return original_output, []

        return wrapper

    return decorator
