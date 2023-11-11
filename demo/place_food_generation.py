import os
import time
from io import BytesIO

import replicate
import requests
from openai import OpenAI
from PIL import Image as PILImage

from yival.logger.token_logger import TokenLogger
from yival.schemas.experiment_config import MultimodalOutput
from yival.states.experiment_state import ExperimentState
from yival.wrappers.string_wrapper import StringWrapper

# Edit place_name and season here~
place_name = "New York"
season = 'Winter'

variation_prompt = """
Generate a prompt with 2-4 different local dish names from {place_name} in {season}, following the format "dish_name_1 | dish_name_2 | dish_name_3".
"""

TOKEN = os.getenv('MIDJOURNEY_TOKEN')  #We have provided this ~
BASE_URL = "https://api.thenextleg.io"

HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json'
}

s = requests.session()


def resize_image(image_content, max_size):
    image = PILImage.open(BytesIO(image_content))
    image.thumbnail(max_size)
    return image


def prompt_generation(prompt: str) -> str:
    '''generate prompt for chatgpt based on the input'''
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
    return res


def post_request(payload):
    '''post request to get messageid'''
    url = f"{BASE_URL}/v2/imagine"
    response = s.post(url, headers=HEADERS, data=payload)
    return response.json()


def get_request(messageId):
    '''get response from messageId'''
    url = f"{BASE_URL}/v2/message/{messageId}?expireMins=2"
    while True:
        time.sleep(2)
        response = s.get(url, headers=HEADERS)
        response_json = response.json()
        if response_json.get('progress') == 100:
            break
    print(f"[INFO] Successfully get response from messageId: {messageId}")
    return response.json()


def video_generation(
    place_name: str, season: str, state: ExperimentState
) -> MultimodalOutput:
    logger = TokenLogger()
    logger.reset()
    # Ensure you have your OpenAI API key set up
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Use the chat-based completion
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role":
            "system",
            "content":
            "You are a helpful assistant that generate stable-diffusion-video prompt."
        }, {
            "role":
            "user",
            "content":
            str(
                StringWrapper(
                    template="""
                Generate a prompt with 2-4 different local dish names from {place_name} in {season}, following the format "dish_name_1 | dish_name_2 | dish_name_3".
                """,
                    variables={
                        "place_name": place_name,
                        "season": season
                    },
                    name="task",
                    state=state
                )
            )
        }]
    )

    prompt = response.choices[0].message.content
    output = replicate.run(
        "nateraw/stable-diffusion-videos:2d87f0f8bc282042002f8d24458bbf588eee5e8d8fffb6fbb10ed48d1dac409e",
        input={"prompts": prompt}
    )
    res = MultimodalOutput(
        text_output=response.choices[0].message.content, video_output=[output]
    )
    if response.usage is not None:
        token_usage = response.usage.total_tokens
    else:
        token_usage = 0
    logger.log(token_usage)
    return res
