import asyncio
import os
import re
from typing import Any, Dict

import aiohttp
# for exponential backoff
import openai
import yaml
from aiohttp_socks import ProxyConnector  # type: ignore
from termcolor import colored

from yival.common.model_utils import llm_completion
from yival.schemas.combination_enhancer_configs import OptimizeByPromptEnhancerConfig
from yival.schemas.data_generator_configs import OpenAIPromptBasedGeneratorConfig
from yival.schemas.dataset_config import DatasetConfig
from yival.schemas.evaluator_config import OpenAIPromptBasedEvaluatorConfig
from yival.schemas.experiment_config import (
    ExperimentConfig,
    HumanRatingConfig,
    WrapperConfig,
    WrapperVariation,
)
from yival.schemas.model_configs import Request
from yival.schemas.selector_strategies import AHPConfig

DATA_GENERATION_PROMPT_TEMPLATE: str = """Generate function descritpion that complete the following task :
    ####
    {task}
    ####
    The function's parameters are: {parameter}

    ### Description only without mentioning parameter and type and description only and nothing else ####
"""

DATA_GENERATION_FUNCTION_NAME_PROMPT_TEMPLATE: str = """Generate proper python function name based on following description :
    ####
    {description}
    ####

    ### Name only and nothing else ####
"""

EVALUATION_ASPECT_GENERATION_PROMPT_TEMPLATE: str = """Generate evaluation descritpion for aspects :
###
{aspect}
###
based on the following task :
{task}

    for example, for the task
        Given an tech startup business, generate one corresponding landing
        page headline
    
    and aspect:
    clarity
    
returns the returned result:

    Does the headline clearly communicate what the startup does or what problem it solves?
    It should be immediately clear to anyone who reads the headline what the startup's purpose is. 
    display_name: clarity

"""

EVALUATION_GENERATION_PROMPT_TEMPLATE: str = """Generate at most 3 important evaluation aspects  that complete the following task :
    ####
    {task}
    ####


    for example, for the task
        Given an tech startup business, generate one corresponding landing
        page headline

        
    The returned task evaluation aspect will be 
    
    Does the headline clearly communicate what the startup does or what problem it solves?
    It should be immediately clear to anyone who reads the headline what the startup's purpose is. 
    display_name: clarity
    
    Is the headline relevant to the target audience? The headline should speak directly to the
    startup's intended users or customers, highlighting the benefits or value proposition that 
    the startup offers
    display_name: relevance
    
    Is the headline catchy or memorable? While it's important to be clear and relevant,
    a good headline should also be engaging and memorable. 
    This can help the startup stand out in a crowded market.    
    display_name: catchy
    
    
    Thoughts: <Think step by step and reflect on each step before you make a decision>
    Aspects: <The aspects goes here>
    
"""

HEAD_META_PROMPT_TEMPLATE: str = """Generate head meata prompt for the task :
    ####
    {task}
    ####
    parameters
    {parameters}

    Below are some examples:
    
    Example 1:
    
    Given an tech startup business, generate one corresponding landing
    page headline for {{tech_startup_business}} specialize in {{business}} and target {{target_people}}
        
    parameters:
        tech_startup_business: str
        business: str
        target_people: str
        
    ==> 

    Now you will help me generate a prompt which is used to generate a corresponding
    landing page headline according for a startup business named [tech_startup_business],
    specializing in [business], and target_peopleing [target_people].
    I already have some prompt and its evaluation results:
    
    Example 2:
    Given the species of an animal and its character, generate a corresponding story
    for {{species}} which is {{character}}
    
    Parameters:
        species: str
        character: str

    ==>
    Now you will help me generate a prompt which is used to generate a corresponding
    story according to the species of an animal which is [species] and its character [character]. 
    I already have some prompt and its evaluation results:
    
    Head meta prompt:
    
"""


def get_evaluation_aspects(aspects: list[str]) -> list[str]:
    return aspects


def extract_variables(text) -> list[str]:
    # Regular expression pattern to find {{variable_name}}
    pattern = r"\{\{(\w+)\}\}"

    # Find all matches and return them as a list
    return re.findall(pattern, text)


def extract_arguments(data):
    # Extract the arguments from the given dictionary
    args_string = data.get("choices",
                           [{}])[0].get("message",
                                        {}).get("function_call",
                                                {}).get("arguments", "")

    # Convert the string representation of arguments into a dictionary
    args_dict = eval(args_string)

    return args_dict


functions = [
    {
        "name": "get_evaluation_aspects",
        "description": "Get the evaluation aspects for a given task",
        "parameters": {
            "type": "object",
            "properties": {
                "description_display_name_map": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "description": {
                                "type": "string",
                                "description": "Evaluation description",
                            },
                            "display_name": {
                                "type": "string",
                                "description": "Display name",
                            },
                        }
                    },
                    "description": "Map from description to display name",
                },
            },
            "required": ["description_display_name_map"],
        },
    },
]


def generate_evaluator_config(
    task: str, evaluation_question: str, display_name: str,
    parameters: list[str]
) -> OpenAIPromptBasedEvaluatorConfig:
    # Generate the prompt string based on the given inputs
    input_parameters = "\n".join([
        f"{param}: {{{{{param}}}}}" for param in parameters
    ])
    prompt = (
        f"You are assessing a submitted answer on a given task based on a criterion. Here is the data:\n"
        f"{task}\n"
        f"{evaluation_question}\n"
        f"[Input]: {input_parameters}\n"
        f"[Result]: {{raw_output}}\n"
        "Answer the question by selecting one of the following options:\n"
        "A It fails to meet the criterion at all.\n"
        "B It somewhat meets the criterion, but there is significant room for improvement.\n"
        "C It meets the criterion to a satisfactory degree.\n"
        "D It meets the criterion very well.\n"
        "E It meets the criterion exceptionally well, with little to no room for improvement."
    )

    # Generate the evaluator configuration
    config = {
        "evaluator_type": "individual",
        "metric_calculators": [{
            "method": "AVERAGE"
        }],
        "name": "openai_prompt_based_evaluator",
        "prompt": prompt,
        "display_name": display_name,
        "description": evaluation_question,
        "scale_description": "0-4",
        "choices": ["A", "B", "C", "D", "E"],
        "choice_scores": {
            "A": 0,
            "B": 1,
            "C": 2,
            "D": 3,
            "E": 4
        }
    }
    config = OpenAIPromptBasedEvaluatorConfig(**config)  # type: ignore
    return config  # type: ignore


def output_aspects_for_eval(response: str) -> str:
    prompt = "Please provide the aspects for evaluation based on \n\n" + response
    response = llm_completion(
        Request(
            model_name="gpt-4",
            prompt=prompt,
            params={
                "functions": functions,
                "temperature": 0
            }
        )
    ).output
    return extract_arguments(response)


async def auto_data_generation_prompt(task: str, parameters: list[str]) -> str:
    parameter = "\n".join(parameters)
    prompt = [{
        "role":
        "user",
        "content":
        DATA_GENERATION_PROMPT_TEMPLATE.format(task=task, parameter=parameter)
    }]
    response = await acompletion(model="gpt-4", messages=prompt, temperature=0)
    return response['choices'][0]['message']['content']


async def auto_data_generation_function_name_prompt(description: str) -> str:
    prompt = [{
        "role":
        "user",
        "content":
        DATA_GENERATION_FUNCTION_NAME_PROMPT_TEMPLATE.format(
            description=description
        )
    }]
    response = await acompletion(model="gpt-4", messages=prompt, temperature=0)
    return response['choices'][0]['message']['content']


async def auto_evaluation_prospect(task: str) -> str:
    prompt = [{
        "role":
        "user",
        "content":
        EVALUATION_GENERATION_PROMPT_TEMPLATE.format(task=task)
    }]
    response = await acompletion(model="gpt-4", messages=prompt, temperature=0)
    return response['choices'][0]['message']['content']


async def generate_manual_aspect(task: str, aspect: str) -> str:
    prompt = [{
        "role":
        "user",
        "content":
        EVALUATION_ASPECT_GENERATION_PROMPT_TEMPLATE.format(
            task=task, aspect=aspect
        )
    }]
    response = await acompletion(model="gpt-4", messages=prompt, temperature=0)
    return response['choices'][0]['message']['content']


async def auto_head_meta_prompt(task: str, parameters: list[str]) -> str:
    parameter = "\n".join(parameters)
    prompt = [{
        "role":
        "user",
        "content":
        HEAD_META_PROMPT_TEMPLATE.format(task=task, parameters=parameter)
    }]
    response = await acompletion(model="gpt-4", messages=prompt, temperature=0)
    return response['choices'][0]['message']['content']


def remove_none_values(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively remove keys with None values from a dictionary.

    Args:
    - data (dict): Input dictionary.

    Returns:
    - dict: A new dictionary with keys with None values removed.
    """
    if not isinstance(data, dict):
        return data

    new_data = {}
    for k, v in data.items():
        if isinstance(v, dict):
            v = remove_none_values(v)
        if v is not None:
            new_data[k] = v
    return new_data


def write_to_yaml(config: ExperimentConfig, filepath: str) -> None:
    data = remove_none_values(config.asdict())
    with open(filepath, 'w') as file:
        yaml.dump(data, file)
    return


async def acompletion(**kwargs):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openai.api_key}",
        "Content-Type": "application/json"
    }

    proxy = os.environ.get("all_proxy")
    if proxy:
        connector = ProxyConnector.from_url(proxy)
    else:
        connector = None
    kwargs.pop('request_timeout', None)

    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.post(url, headers=headers, json=kwargs) as response:
            return await response.json()


async def auto_generate_config(
    prompt: str, additional_aspect: list[str]
) -> None:
    parameters = extract_variables(prompt)
    description_task = asyncio.create_task(
        auto_data_generation_prompt(prompt, parameters)
    )
    function_name_task = asyncio.create_task(
        auto_data_generation_function_name_prompt(prompt)
    )
    description, function_name = await asyncio.gather(
        description_task, function_name_task
    )

    parameters_dict = {}
    for p in parameters:
        parameters_dict[p] = "str"
    generator_config = OpenAIPromptBasedGeneratorConfig(
        chunk_size=10000,
        number_of_examples=5,
        output_path=function_name + "_generated_data.pkl",
        output_csv_path=function_name + "_generated_data.csv",
        single_shot=True,
        diversify=False,
        input_function={
            "description": description,
            "name": function_name,
            "parameters": parameters_dict
        },
    )

    dataset_config = DatasetConfig(
        source_type="machine_generated",  # type: ignore
        data_generators={"openai_prompt_data_generator": generator_config}
    )
    print(colored("\n[INFO] Generate evaluation aspects", "green"))
    # evaulation_prospect = auto_evaluation_prospect(description)
    # if len(additional_aspect) > 0:
    #     for aspect in additional_aspect:
    #         new_aspect = generate_manual_aspect(prompt, aspect)
    #         evaulation_prospect += '\n' + new_aspect

    evaluation_prospect_task = asyncio.create_task(
        auto_evaluation_prospect(description)
    )
    aspect_tasks = [
        asyncio.create_task(generate_manual_aspect(prompt, aspect))
        for aspect in additional_aspect if aspect
    ]
    aspects = await asyncio.gather(*aspect_tasks)
    evaluation_prospect = await evaluation_prospect_task
    evaluation_prospect += '\n' + '\n'.join(aspects)
    evaulation_prospect_dict = output_aspects_for_eval(evaluation_prospect)

    head_meta_prompt = await auto_head_meta_prompt(prompt, parameters)

    evaulator_configs: list[OpenAIPromptBasedEvaluatorConfig] = []
    human_rating_configs: list[HumanRatingConfig] = []

    variation_config = WrapperConfig(
        name="task",
        variations=[WrapperVariation(value_type="str", value=prompt)]
    )
    end_meta_message = "Give me a new prompt that is different from all pairs above, and has evaluation values on "

    # and has evaluation values on accuracy, relevance, intrigue, emoji, cute, that are higher than any of above.
    for eval in evaulation_prospect_dict[
        "description_display_name_map"  # type: ignore
    ]:  # type: ignore
        evaulator_configs.append(
            generate_evaluator_config(
                description,
                eval["description"],  # type: ignore
                eval["display_name"],  # type: ignore
                parameters
            )
        )
        end_meta_message += eval["display_name"] + ", "  # type: ignore
        human_rating_configs.append(
            HumanRatingConfig( # type: ignore
                name=eval["display_name"],  # type: ignore
                instructions=eval["description"],  # type: ignore
                scale=[0, 4]  # type: ignore
            )
        )
    end_meta_message += "that are higher than any of above."
    # additional_message = "And make sure it has the list of parameters "
    # for p in parameters:
    #     additional_message = additional_message + '{' + p + '}  '
    enhancer_config = OptimizeByPromptEnhancerConfig(
        name="optimize_by_prompt_enhancer",
        enhance_var=["task"],
        head_meta_instruction=head_meta_prompt,
        end_meta_instruction=end_meta_message,
        model_name="gpt-4",
        max_iterations=2
    )
    criteria = []
    criteria_weights = {}
    criteria_maximization = {
        "average_token_usage": False,
        "average_latency": False
    }
    for _, eval in enumerate(evaulator_configs):  # type: ignore
        criteria.append(eval.name + ": " + eval.display_name)  # type: ignore
        criteria_maximization[eval.name + ": " +  # type: ignore
                              eval.display_name] = True  # type: ignore
        criteria_weights[
            eval.name + ": " +  # type: ignore
            eval.display_name] = 1.0 / len(evaulator_configs)  # type: ignore
    criteria.append("average_token_usage")
    criteria.append("average_latency")
    criteria_weights["average_latency"] = 0
    criteria_weights["average_token_usage"] = 0

    ahp_selection = AHPConfig(
        criteria=criteria,
        criteria_weights=criteria_weights,
        criteria_maximization=criteria_maximization,
    )
    config = ExperimentConfig(
        description="Auto generated config for " + prompt,
        human_rating_configs=human_rating_configs,
        dataset=dataset_config,
        evaluators=evaulator_configs,  # type: ignore
        custom_function="demo.complete_task.complete_task",
        variations=[variation_config],
        enhancer=enhancer_config,
        selection_strategy={"ahp_selection": ahp_selection}
    )
    write_to_yaml(config, "auto_generated_config.yaml")


def main():
    test = """
        Given generate a short tiktok video title based on the following info\ncontent_summary:
        {{content_summary}}\ntarget_audience: {{target_audience}}    
    """
    asyncio.run(auto_generate_config(test, ["has emojis", "is cute"]))
    # print(
    #     generate_manual_aspect(
    #         "generate first paragraph of an email", "humble tone"
    #     )
    #)
    # #print(res)
    # # res = auto_evaluation_prospect(
    # #     "The function is designed to create a script for TikTok videos. It takes into consideration the specific topic of the content as well as the target audience for whom the TikTok video is created. It uses this information to draft a suitable, engaging and relevant script for the making TikTok video based on the provided content topic and audience preferences. The function is useful for those looking to create tailored content suitable for their audience on the TikTok platform."
    # # )
    # # print(res)
    # # print(output_aspects_for_eval(res))
    # config = generate_evaluator_config(
    #     "Given an tech startup business, generate one corresponding landing page headline",
    #     "Is the headline relevant to the target audience?",
    #     tech_startup_business="ExampleTech",
    #     business="Tech Solutions",
    #     target_people="Tech Enthusiasts"
    # )


# print(auto_head_meta_prompt("tiktok script writer", ["tiktok_cotnent_topic", "ticktok_audience"]))

if __name__ == "__main__":
    main()
