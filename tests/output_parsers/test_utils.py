from yival.output_parsers.base_parser import BaseParserWithRegistry
from yival.output_parsers.utils import capture_and_parse_with_base_registry


class TestParser(BaseParserWithRegistry):

    def parse(self, output: str) -> list[str]:
        return ["Parsed: " + output]


def test_modified_decorator_without_parser():

    @capture_and_parse_with_base_registry()
    def function_without_parser():
        print("Message from function_without_parser")
        return "Return Value from function_without_parser"

    original_output, logs = function_without_parser()
    assert original_output == "Return Value from function_without_parser"
    assert len(logs) == 0
