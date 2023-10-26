from typing import Dict, List


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