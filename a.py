PROMPT_DESCRIPTION = """
## Prompt
{prompt}

## Full Template
This describes how the prompt of interested is concatenated with the input text.
```
{{full_prompt_description}}
```

## Examples
{{examples}}

## Instructions
For some of these examples, the output does not match with the task. This may be due to the prompt
being misleading or not describing the task precisely.

Please examine the examples carefully. For each example, providing reasoning according to the following template:

### Example <id>
Input: <input>
Output: <output>
Label: <label>
Is the output correctly following the given prompt: <yes or no, and your reasoning>
To output the correct label, is it necessary to edit the prompt: <yes or no, and your reasoning>
If yes, provide detailed analysis and actionable suggestions to edit the prompt: <analysis and suggestions>.
"""

a = PROMPT_DESCRIPTION.format(
    prompt="abc",
    full_prompt_description="abc",
    examples="abc"
)

print(a)