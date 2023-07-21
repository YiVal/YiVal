from .base_parser import BaseParserWithRegistry
from .utils import capture_and_parse_with_base_registry


class TestParser(BaseParserWithRegistry):
    def parse(self, output):
        return ["Parsed: " + output]


def test_decorator_with_parser_diagnostic():
    config = {"parser": "TestParser"}

    @capture_and_parse_with_base_registry(config)
    def function_with_parser():
        print("Message from function_with_parser")
        return "Return Value from function_with_parser"

    original_output, logs = function_with_parser()
    print(f"Captured Logs (With Parser): {logs}")  # Diagnostic print
    assert original_output == "Return Value from function_with_parser"
    assert len(logs) == 1
    assert logs[0] == "Parsed: Message from function_with_parser\n"


def test_modified_decorator_without_parser():
    @capture_and_parse_with_base_registry()
    def function_without_parser():
        print("Message from function_without_parser")
        return "Return Value from function_without_parser"

    original_output, logs = function_without_parser()
    assert original_output == "Return Value from function_without_parser"
    assert len(logs) == 0
