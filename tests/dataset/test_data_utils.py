from yival.dataset.data_utils import _tokenize_condition


class ExperimentResult:

    def __init__(self, combination={}, input_data=None, raw_output=None):
        self.combination = combination
        self.input_data = input_data
        self.raw_output = raw_output


def test_tokenize_condition():
    condition = "name == openai_prompt_based_evaluator AND result >= 3 OR display_name != clarity"
    tokens = _tokenize_condition(condition)
    expected = [
        'name', '==', 'openai_prompt_based_evaluator', 'AND', 'result', '>=',
        '3', 'OR', 'display_name', '!=', 'clarity'
    ]
    assert tokens == expected
