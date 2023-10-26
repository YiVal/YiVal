import pytest

from yival.output_parsers.base_parser import BaseParserWithRegistry


def test_subclass_registration():
    # Define a new subclass
    class TestParser(BaseParserWithRegistry):

        def parse(self, output: str) -> list[str]:
            return [output]

    # Ensure the subclass is registered
    assert "TestParser" in BaseParserWithRegistry.registry
    assert BaseParserWithRegistry.registry["TestParser"] == TestParser


def test_multiple_subclass_registration():
    # Define multiple subclasses
    class TestParser1(BaseParserWithRegistry):

        def parse(self, output: str) -> list[str]:
            return [output]

    class TestParser2(BaseParserWithRegistry):

        def parse(self, output: str) -> list[str]:
            return [output, output]

    # Ensure the subclasses are registered
    assert "TestParser1" in BaseParserWithRegistry.registry
    assert BaseParserWithRegistry.registry["TestParser1"] == TestParser1

    assert "TestParser2" in BaseParserWithRegistry.registry
    assert BaseParserWithRegistry.registry["TestParser2"] == TestParser2


def test_parse_not_implemented():
    # Define a subclass without overriding the parse method
    class TestParser(BaseParserWithRegistry):
        pass

    parser = TestParser()

    with pytest.raises(NotImplementedError):
        parser.parse("test")
