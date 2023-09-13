import importlib
import os
import re
from typing import Any, Callable, Dict, List, Optional

from yival.schemas.experiment_config import EvaluatorOutput, ExperimentResult

# Define the comparison operators
COMPARISON_OPERATORS: Dict[str, Callable[[Any, Any], bool]] = {
    "==": lambda x, y: x == y,
    "<": lambda x, y: x < y,
    ">": lambda x, y: x > y,
    "<=": lambda x, y: x <= y,
    "!=": lambda x, y: x != y
}


def _tokenize_condition(condition: str) -> List[str]:
    """
    Tokenize a condition string into its components.
    This version handles compound operators like >=, <=.

    Args:
    - condition (str): The condition string.

    Returns:
    - List[str]: The tokenized condition.
    """

    # Replace logical operators with placeholders
    condition = condition.replace(" AND ", " &AND& ")
    condition = condition.replace(" OR ", " &OR& ")
    condition = condition.replace(" NOT ", " &NOT& ")
    condition = condition.replace("(", " ( ")
    condition = condition.replace(")", " ) ")

    # Tokenize based on spaces
    tokens = condition.split()

    # Convert placeholders back to their original form
    tokens = [
        "AND" if token == "&AND&" else
        "OR" if token == "&OR&" else "NOT" if token == "&NOT&" else token
        for token in tokens
    ]

    # Handle compound operators by merging tokens
    i = 0
    while i < len(tokens) - 1:
        if tokens[i] in [">", "<", "=", "!"] and tokens[i + 1] == "=":
            tokens[i] = tokens[i] + "="
            tokens.pop(i + 1)
        i += 1

    return tokens


def _evaluate_condition(
    evaluator_output: EvaluatorOutput, condition: str
) -> bool:
    """
    Evaluate a condition against an evaluator output, enhanced version 3.

    Args:
    - evaluator_output (EvaluatorOutput): The evaluator output to evaluate against.
    - condition (str): The condition to evaluate.

    Returns:
    - bool: True if the condition is met, otherwise False.
    """

    # Split the condition into its components
    parts = condition.split(" ")
    if len(parts) != 3:
        raise ValueError(f"Invalid condition format: {condition}")

    field_path, operator, value = parts

    # Split the field path into its components
    field_name, sub_field_name = field_path.split(
        ":"
    ) if ":" in field_path else (field_path, None)

    # Fetch the actual value from the evaluator output based on the field path
    actual_value = None
    if field_name == "name":
        actual_value = evaluator_output.name
    elif field_name == "display_name":
        actual_value = evaluator_output.display_name
    elif field_name == "result":
        actual_value = evaluator_output.result
    else:
        raise ValueError(f"Unknown field name: {field_name}")

    # Convert the value to the appropriate type
    if isinstance(actual_value, int):
        value = int(value)
    elif isinstance(actual_value, float):
        value = float(value)

    # Define the comparison operators
    COMPARISON_OPERATORS = {
        "==": lambda x, y: x == y,
        "!=": lambda x, y: x != y,
        "<": lambda x, y: x < y,
        "<=": lambda x, y: x <= y,
        ">": lambda x, y: x > y,
        ">=": lambda x, y: x >= y
    }

    # Evaluate the condition using the specified operator
    if operator not in COMPARISON_OPERATORS:
        raise ValueError(f"Unknown operator: {operator}")

    return COMPARISON_OPERATORS[operator](actual_value, value)


def _evaluate_tokenized_condition(
    tokens: List[str], evaluator_output: EvaluatorOutput
) -> bool:
    """
    Evaluate a tokenized condition using a stack-based approach, version 14.

    Args:
    - tokens (List[str]): The tokenized condition.
    - evaluator_output (EvaluatorOutput): The evaluator output to evaluate against.

    Returns:
    - bool: True if the condition is met, otherwise False.
    """

    stack: List[Any] = []
    for token in tokens:
        if token == '(':
            stack.append(token)
        elif token in ["True", "False"]:
            stack.append(token == "True")
        elif token == ')':
            # Pop elements from the stack until the matching '(' is found
            temp_tokens: List[Any] = []
            while stack and stack[-1] != '(':
                temp_tokens.insert(0, stack.pop())
            # Pop the '(' token
            if stack and stack[-1] == '(':
                stack.pop()
            else:
                raise ValueError("Mismatched parentheses in condition")
            inner_result = _evaluate_tokenized_condition(
                temp_tokens, evaluator_output
            )
            stack.append(inner_result)
        else:
            stack.append(token)

    # Process the remaining tokens in the stack
    while len(stack) > 1:
        # Handle the NOT operator
        if stack[0] == "NOT":
            stack.pop(0)
            operand = stack.pop(0)
            if isinstance(operand, bool):
                operand_result = operand
            else:
                operand_tokens = [operand]
                while stack and stack[0] not in ["AND", "OR", "NOT"]:
                    operand_tokens.append(stack.pop(0))
                operand_result = _evaluate_condition(
                    evaluator_output, " ".join(operand_tokens)
                )
            stack.insert(0, not operand_result)
            continue

        # Extract the left-most condition or result from the stack
        left = stack.pop(0)

        # If left is a boolean, it's the result of a previous evaluation
        if isinstance(left, bool):
            left_result = left
        else:
            # Otherwise, extract the full condition from the stack until a logical operator is found
            left_tokens = [left]
            while stack and stack[0] not in ["AND", "OR", "NOT"]:
                left_tokens.append(stack.pop(0))
            left_result = _evaluate_condition(
                evaluator_output, " ".join(left_tokens)
            )

        # Extract the operator
        operator = stack.pop(0)

        # Extract the right-most condition or result from the stack (if applicable)
        right = stack.pop(0)
        # If right is a boolean, it's the result of a previous evaluation
        if isinstance(right, bool):
            right_result = right
        else:
            # Otherwise, extract the full condition from the stack until another logical operator or the end is found
            right_tokens = [right]
            while stack and stack[0] not in ["AND", "OR", "NOT"]:
                right_tokens.append(stack.pop(0))
            right_result = _evaluate_condition(
                evaluator_output, " ".join(right_tokens)
            )

        # Evaluate using the operator and push the result back onto the stack
        if operator == "AND":
            stack.insert(0, left_result and right_result)
        elif operator == "OR":
            stack.insert(0, left_result or right_result)

    # Return the final result
    return stack[0]


def evaluate_condition(
    condition: str, evaluator_output: EvaluatorOutput
) -> bool:
    tokens = _tokenize_condition(condition)
    return _evaluate_tokenized_condition(tokens, evaluator_output)


def read_code_from_path_or_module(path_or_module: str) -> Optional[str]:
    """
    Reads the source code either from an absolute file path or from a module, refined version.
    
    Args:
    - path_or_module (str): Either an absolute path to a Python file or a module name.
    
    Returns:
    - Optional[str]: The source code if found, otherwise None.
    """
    # If it's a path, try reading the file
    if os.path.exists(path_or_module) and path_or_module.endswith('.py'):
        with open(path_or_module, 'r') as file:
            return file.read()

    # If it's a module, try importing and getting the source from its path
    else:
        try:
            module = importlib.import_module(path_or_module)
            module_path = module.__file__
            assert module_path
            # Read the content of the module file
            with open(module_path, 'r') as file:
                return file.read()
        except Exception:
            # Failed to import or get the source, return None
            return None


def transform_experiment_result_generic(
    code: str, exp_result: ExperimentResult
):
    # Extracting the namespace from the code using a regex for any **Wrapper pattern
    wrapper_pattern = r"(\w+Wrapper)\(.*?name=\"(\w+)\".*?\)"
    matches = re.search(wrapper_pattern, code, re.DOTALL)

    # If no matches found, return None
    if not matches:
        return None

    # Extract the namespace from the matched pattern
    namespace = matches.group(2)

    # Extract the combination's value for the found namespace
    combo_value = exp_result.combination.get(namespace, "")

    # If no combination value found for the namespace, return None
    if not combo_value:
        return None
    # Format the combination's value using the content in input_data.content
    variable_pattern = r"\{(\w+)\}"
    variables_in_combo = re.findall(variable_pattern, combo_value)

    if not variables_in_combo or not all(
        var in exp_result.input_data.content for var in variables_in_combo
    ):
        return {
            "Instruction": combo_value,
            "Input": exp_result.input_data.content,
            "Output": exp_result.raw_output
        }
    formatted_input = combo_value.format(**exp_result.input_data.content)

    # Construct the final pair

    if isinstance(exp_result.raw_output, str):
        output = exp_result.raw_output.strip('"')
    else:
        output = exp_result.raw_output
    result_pair = {"Input": formatted_input, "Output": output}

    return result_pair


def main():
    code = read_code_from_path_or_module("yival.demo.headline_generation")
    import pickle

    from yival.schemas.experiment_config import Experiment
    condition = "name == openai_prompt_based_evaluator AND result >= 3 AND display_name == clarity "
    with open('test_demo_results.pkl', 'rb') as f:
        result: Experiment = pickle.load(f)
    for combo_result in result.combination_aggregated_metrics:
        results: List[ExperimentResult] = combo_result.experiment_results
        for result in results:
            for eo in result.evaluator_outputs:
                condition_met = evaluate_condition(condition, eo)
                if condition_met:
                    result_pair = transform_experiment_result_generic(
                        code, result
                    )
                    print(result_pair)


if __name__ == "__main__":
    main()
