import re
from typing import Dict, List, Tuple, Union

from ..common.model_utils import llm_completion
from ..schemas.experiment_config import Experiment, ExperimentResult
from ..schemas.model_configs import Request


def find_origin_combo_key(experiment: Experiment) -> str:
    """
    Find the combo key from best_combination
    Ensure that we have selector config
    """
    if experiment.selection_output is not None:
        combo_key = experiment.selection_output.best_combination
        return combo_key
    else:
        raise ValueError("Selection output is None")


def format_input_from_dict(input_dict: Dict, enhance_var: List[str]) -> str:
    """
    construct input str

    e.g.
    input_dict = {"var1":"hello world", "var2":"bye"} , enhance_var=["var1","var2"]
    
    result:
        var1=hello world
        var2=bye
    """
    result = ""
    for var in enhance_var:
        result = result + f"{var}={input_dict[var]}\n"
    return result


def scratch_variations_from_str(
    target_str: str, variations: List[str]
) -> Dict:
    """
    scratch generate variations from llm_output

    e.g.
    target_str:
        This is the generated new output
        var1=hello world
        hello world
        var2=bye
    
    variations: ["var1", "var2"]

    function result:
    {
        "var1": "hello world\nhello world"
        "var2": "bye"
    }
    """
    result = {var: "" for var in variations}
    lines = target_str.split('\n')
    var_detect = False
    current_var = ""
    for line in lines:
        var_line = False
        for var in variations:
            if line.strip().startswith(f"{var}="):
                var_detect = True
                result[var] = line.strip().split('=',
                                                 1)[1].strip().strip("'\"")
                var_line = True
                current_var = var
        if var_line:
            continue
        if var_detect:
            result[current_var] += ('\n' + line.strip())
    return result


def construct_output_format(variations: List[str]) -> str:
    """
    Instruct llm to output variations in fixed format

    e.g. variations: ["prompt"]

    expected llm output:
        prompt: "123"
    
    function_output:
        Do not write code . Please response with given format:
        prompt={ your generated prompt } 
    """

    prompt = "Do not write code. Please response with given format:\n"
    for var in variations:
        prompt += (var + '=' + '{' + "your generated " + f"{var}" + '}')
    return prompt


def construct_template_restrict(template_vars: List[str]) -> str:
    """
    Restrict llm to output variations in format template

    e.g. template_vars: ['user_info']

    retrict_prompt: 
        Please follow python's template formatting for replies and make sure your output conforms to the format of python string.
        * Use {user_info} instead of user_info
    """

    prompt = "Please follow python's template formatting for replies and make sure your output conforms to the format of python string.\n"
    for var in template_vars:
        prompt += f"* Use {{{var}}} instead of {var}\n"
    return prompt + '\n'


def scratch_template_vars(prompt: str) -> List[str]:
    """
    scratch template vars from given prompt.

    e.g. prompt: write a short discord welcome message based on the following info\n user_info: {user_info}\n channel_type: {channel_type}

    response: ['user_info', 'channel_type']

    """
    return re.findall(r"\{(\w+)\}", prompt)


def openai_call(
    dialogues: Union[str, List[Dict[str, str]]],
    model_name="gpt-3.5-turbo"
) -> str:
    response = llm_completion(
        Request(
            model_name=model_name,
            prompt=dialogues,
            params={"temperature": 0.5}
        )
    ).output
    llm_output_str = response["choices"][0]["message"]["content"]
    return llm_output_str


def extract_from_experiment_result(exp_result: ExperimentResult) -> str:
    input = exp_result.input_data.content
    output = exp_result.raw_output.text_output
    evaluate_str = ""
    assert exp_result.evaluator_outputs is not None
    for eval in exp_result.evaluator_outputs:
        evaluate_str = evaluate_str + f"* {eval.name}-{eval.display_name} score: {eval.result}\n"
    result = f"input:{input}\noutput:{output}\nevaluate result:{evaluate_str}"
    return result


def construct_solution_score_pairs(
    cache: List[Tuple[Dict, Dict]], enhance_var: List[str]
) -> str:
    """
    Construct the solution_score_pairs for the full prompt.
    This part will be longer after each iteration.
    To avoid the input is too long for llm , we will cut the cache to the
    latest five outputs
    """
    prompt = ""
    for prompt_dict, eval_dict in cache[-5:]:
        prompt += 'Input:\n'
        prompt += format_input_from_dict(prompt_dict, enhance_var)
        prompt += 'Evaluation:\n'
        for evaluator_name, score in eval_dict.items():
            display = evaluator_name.split(":")[-1].strip()
            if display == "average_token_usage" or display == "average_latency":
                continue
            prompt += f"{display}: {score} "
        prompt += '\n'

    return prompt


if __name__ == "__main__":
    input = """
    This is the generated new output
            var1= hello world
            hello world
            var2= bye
    """
    print(input)
    result = scratch_variations_from_str(input, ["var1", "var2"])
    print(result)