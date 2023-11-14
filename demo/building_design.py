'''This script is used to generate image from a building design prompt'''

import os
from io import BytesIO

import requests
from openai import OpenAI
from PIL import Image

from yival.logger.token_logger import TokenLogger
from yival.schemas.experiment_config import MultimodalOutput
from yival.states.experiment_state import ExperimentState
from yival.wrappers.string_wrapper import StringWrapper


def prompt_generation(prompt: str) -> str:
    '''generate prompt for chatgpt based on the input'''
    logger = TokenLogger()
    logger.reset()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": prompt
        }],
        temperature=1.0,
        max_tokens=3000
    )
    if response.choices[0].message.content is not None:
        res = str(response.choices[0].message.content[:1000])
    else:
        res = "No content found"

    if response.usage is not None:
        token_usage = response.usage.total_tokens
    else:
        token_usage = 0
    logger.log(token_usage)
    return res


def load_image(images):
    '''load image from response'''
    print("[INFO] start load images")

    image_dict = {}
    for image in images:
        image_url = image.url
        try:
            response = requests.get(image_url)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                image_dict[image_url] = image
            else:
                print(
                    f"[Error] Failed to load image from {image_url}. Response code: {response.status_code}"
                )
        except Exception as e:
            print(
                f"[Error] Failed to load image from {image_url}. Error: {str(e)}"
            )

    print("[INFO] Successfully load images.")
    return image_dict


def building_design(location: str, function: str, state: ExperimentState):
    # Ensure you have your OpenAI API key set up
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = prompt_generation(
        str(
            StringWrapper(
                "Generate a building design for a building",
                name="task",
                variables={
                    "location": location,
                    "function": function,
                },
                state=state
            )
        )
    )

    response = client.images.generate(
        model="dall-e-3", prompt=prompt, n=1, size="1024x1024"
    )
    print(f"\nresponse: {response}\n")
    image_res = MultimodalOutput(
        #     text_output=response.data.revised_prompt,
        text_output=prompt,
        image_output=load_image(response.data),
    )
    return image_res


def main():
    '''main function'''
    location = "New York"
    function = "office"
    state = ExperimentState()
    print(building_design(location, function, state))


if __name__ == "__main__":
    main()
